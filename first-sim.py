import argparse
import carla
import cv2
import logging
import carla
from carla import ColorConverter as cc
import numpy as np
import time
import datetime
import weakref
import math
import os
import sys
import glob
import random
import pygame
import pandas as  pd
from PIL import Image
from queue import Queue
from queue import Empty

import carla_vehicle_annotator as cva


def parser():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=300,
        type=int,
        help='number of vehicles (default: 30)')
    argparser.add_argument(
        '-d', '--number-of-dangerous-vehicles',
        metavar='N',
        default=1,
        type=int,
        help='number of dangerous vehicles (default: 3)')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--sync',
        action='store_true',
        default=True,
        help='Synchronous mode execution')

    return argparser.parse_args()


def sensor_callback(sensor_data, sensor_queue, sensor_name, world):
    if 'radar' in sensor_name:
         points = np.frombuffer(sensor_data.raw_data,dtype=np.dtype('f4'))
         points = np.reshape(points, (-1, 4))
         # outputImgPath="../output/"
         # filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
         # f2 = open(outputImgPath+filename+'.txt','a')
         # f2.write(str(points))
         current_rot = sensor_data.transform.rotation
         debug = world.debug 
         lists=[]
         for detect in sensor_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            if abs(detect.velocity)>0 :
              lists.append([azi,detect.depth,detect.velocity])
              # lists.append(detect.depth)
              # lists.append(detect.velocity)
              # lists = np.reshape(lists, (-1, 3))
              outputImgPath="./output/"
              filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
              # data1=pd.DataFrame(list)
              # data1.to_csv(outputImgPath+filename+'.csv','w')
              f2 = open(outputImgPath+filename+'.txt','w')
              f2.write(str(lists))
            # The 0.25 adjusts a bit the distance so the dots can
            # be properly seen
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll)).transform(fw_vec)

            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))

            norm_velocity = detect.velocity / 7.5 # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
            debug.draw_point(
                sensor_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b))
    if 'camera' in sensor_name:
         array = np.frombuffer(sensor_data.raw_data, dtype=np.dtype("uint8"))
         array = np.reshape(array, (1080, 1920, 4))
         array = array[:, :, :3]
         array = array[:, :, ::-1]
         # array = pygame.surfarray.make_surface(array.swapaxes(0, 1))
         im = Image.fromarray(array)
         outputImgPath="./output/"
         filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
         im.save(outputImgPath+str(filename)+'.jpg')
        # sensor_data.save_to_disk(os.path.join('../outputs/output_synchronized', '%06d.png' % sensor_data.frame))
    sensor_queue.put((sensor_data.frame, sensor_name))


def main():
    args = parser()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_id_list = []
    sensor_list = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False

    try:    
        world = client.load_world('Town03')
        origin_settings = world.get_settings()
        traffic_manager = client.get_trafficmanager(args.tm_port)
        # every vehicle keeps a distance of 3.0 meter
        traffic_manager.set_global_distance_to_leading_vehicle(3.0)
        # Set physical mode only for cars around ego vehicle to save computation
        traffic_manager.set_synchronous_mode(True)
        # default speed is 30
        traffic_manager.global_percentage_speed_difference(-50)
        
        # Suggest using syncmode
        if args.sync:
            settings = world.get_settings()
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                # 25fps
                settings.fixed_delta_seconds = 0.04
                world.apply_settings(settings)
        blueprints_vehicle = world.get_blueprint_library().filter("vehicle.*")
        # sort the vehicle list by id
        blueprints_vehicle = sorted(blueprints_vehicle, key=lambda bp: bp.id)
        print (blueprints_vehicle)
        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles >= number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points - 1

        # Use command to apply actions on batch of data
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        # this is equal to int 0
        FutureActor = carla.command.FutureActor

        batch = []

        for n, transform in enumerate(spawn_points):
            if n >= args.number_of_vehicles:
                break

            blueprint = random.choice(blueprints_vehicle)

            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)

            # set autopilot
            blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot all together
            batch.append(SpawnActor(blueprint, transform)
                         .then(SetAutopilot(FutureActor, True)))

        # excute the command
        for (i, response) in enumerate(client.apply_batch_sync(batch, synchronous_master)):
            if response.error:
                logging.error(response.error)
            else:
                print("Fucture Actor", response.actor_id)
                vehicles_id_list.append(response.actor_id)

        vehicles_list = world.get_actors().filter('vehicle.*')
        # wait for a tick to ensure client receives the last transform of the vehicles we have just created
        if not args.sync or not synchronous_master:
            world.wait_for_tick()
        else:
            world.tick()
        
        # set several of the cars as normal car
        for i in range(args.number_of_vehicles):
            car = vehicles_list[i]
            traffic_manager.distance_to_leading_vehicle(car, 3)
            traffic_manager.vehicle_percentage_speed_difference(car, -80)


        

        # set several of the cars as dangerous car
        for i in range(args.number_of_dangerous_vehicles):
            danger_car = vehicles_list[i]
            # crazy car ignore traffic light, do not keep safe distance, and very fast
            traffic_manager.ignore_lights_percentage(danger_car, 100)
            traffic_manager.distance_to_leading_vehicle(danger_car, 0)
            traffic_manager.vehicle_percentage_speed_difference(danger_car, -100)

        print('spawned %d vehicles , press Ctrl+C to exit.' % (len(vehicles_list)))

        # create ego vehicle
        ego_vehicle_bp = world.get_blueprint_library().filter('model3')[0]
        # green color
        ego_vehicle_bp.set_attribute('color', '0, 0, 0')
        # set this one as ego
        ego_vehicle_bp.set_attribute('role_name', 'hero')
        # get a valid transform that has not been assigned yet
        transform = spawn_points[len(vehicles_id_list)]

        ego_vehicle = world.spawn_actor(ego_vehicle_bp, transform)
        ego_vehicle.set_autopilot(True)
        vehicles_id_list.append(ego_vehicle.id)

        # create sensor queue
        sensor_queue = Queue(maxsize=10)

        # add a camera
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(1920))
        camera_bp.set_attribute('image_size_y', str(1080))
        camera_bp.set_attribute('fov', '60')
        camera_bp.set_attribute('sensor_tick', str(0.04))
        # camera relative position related to the vehicle

        # Manually selected camera location
        camera_transform = carla.Transform(carla.Location(-82.615005, -138.925934, 12.720448), carla.Rotation(-14.151550, 89.400490, -0.000276))
        camera = world.spawn_actor(camera_bp, camera_transform)
        # set the callback function
        camera.listen(lambda image_data: sensor_callback(image_data, sensor_queue, "camera",world))
        sensor_list.append(camera)

        # # we also add a radar on it
        # rad_bp = world.get_blueprint_library().find('sensor.other.radar')
        # rad_bp.set_attribute('horizontal_fov', str(30))
        # rad_bp.set_attribute('vertical_fov', str(30))
        # rad_bp.set_attribute('range', str(76))
        # rad_bp.set_attribute('sensor_tick', str(0.04)) 
        # rad_bp.set_attribute('points_per_second', str(500))
        # # set the relative location
        # radar_location = carla.Location(0, 0, 2)
        # radar_rotation = carla.Rotation(0, 0, 0)
        # radar_transform = carla.Transform(radar_location, radar_rotation)
        # # spawn the radar
        # radar = world.spawn_actor(rad_bp, transform)
        # radar.listen(
        #     lambda radar_data: sensor_callback(radar_data, sensor_queue, "radar", world))
        # sensor_list.append(radar)

        while True:
            if args.sync and synchronous_master:
                world.tick()
               # set the sectator to follow the ego vehicle
                spectator = world.get_spectator()
                # transform = ego_vehicle.get_transform()
                spectator.set_transform(transform)
                try:
                    for i in range(0, len(sensor_list)):
                        s_frame = sensor_queue.get(True, 1.0)
                        print("    Frame: %d   Sensor: %s" % (s_frame[0], s_frame[1]))
                except Empty:
                    print("   Some of the sensor information is missed")
            else:
                world.wait_for_tick()

    finally:
        world.apply_settings(origin_settings)
        print('\ndestroying %d vehicles' % len(vehicles_id_list))

        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_id_list])
        for sensor in sensor_list:
            sensor.destroy()
        print('done.')


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')
