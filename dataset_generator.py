## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

import glob
import os
import sys
import time

from numpy.lib.function_base import select

# try:
#     sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
#         sys.version_info.major,
#         sys.version_info.minor,
#         'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
# except IndexError:
#     print('carla not found')
#     pass

import carla

import argparse
import logging
import random
import queue
import numpy as np
from matplotlib import pyplot as plt
import cv2
import carla_vehicle_annotator as cva
from tqdm import tqdm

def retrieve_data(sensor_queue, frame, timeout=5):
    while True:
        try:
            data = sensor_queue.get(True,timeout)
        except queue.Empty:
            return None
        if data.frame == frame:
            return data


class dataset_generator:
    
    def __init__(self, num_vehicles, world_map, tick_sensor):
        # parameters for saving sensor data
        # TODO: can be improved by reading them from yaml file
        self.save_rgb = True
        self.save_depth = False
        self.save_segm = False
        self.save_lidar = False
        self.tick_sensor = tick_sensor
        self.host = '127.0.0.1'
        self.port = 2000
        self.tm_port = 8000
        self.num_vehicles = num_vehicles

        
        self.vehicles_list = []
        self.nonvehicles_list = []
        self.client = carla.Client(self.host, self.port)
        self.client.set_timeout(10.0)

        self.traffic_manager = self.client.get_trafficmanager(self.tm_port)
        self.traffic_manager.set_global_distance_to_leading_vehicle(2.0)
        self.world = self.client.load_world(world_map)
        self.settings = self.world.get_settings()

        # set
        print('\nRUNNING in synchronous mode\n')
        self.settings = self.world.get_settings()
        
        self.traffic_manager.set_synchronous_mode(True)
        if not self.settings.synchronous_mode:
            self.synchronous_master = True
            self.settings.synchronous_mode = True
            self.settings.fixed_delta_seconds = 0.05
            self.world.apply_settings(self.settings)
        else:
            self.synchronous_master = False
        
        print(self.settings.fixed_delta_seconds)

        self.blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        self.spawn_points = self.world.get_map().get_spawn_points()
        self.num_spawn_points = len(self.spawn_points)

        if self.num_vehicles < self.num_spawn_points:
            random.shuffle(self.spawn_points)
        elif self.num_vehicles > self.num_spawn_points:
            msg = 'Requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, self.num_vehicles, self.num_spawn_points)
            self.num_vehicles = self.num_spawn_points

        self.SpawnActor = carla.command.SpawnActor
        self.SetAutopilot = carla.command.SetAutopilot
        self.FutureActor = carla.command.FutureActor


    def start_simulation(self, cam_t, cam_o, is_in_darknet, num_images):
        '''Start the simulation

        Args:
            cam_t: the translation of spawn location of camera (carla.Location)
            can_o: the rotation of spawn location of camera (carla.Rotation)
        '''
        try:
            # Spawn vehicles
            batch = []
            for n, transform in enumerate(self.spawn_points):
                if n >= self.num_vehicles:
                    break
                blueprint = random.choice(self.blueprints)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                blueprint.set_attribute('role_name', 'autopilot')
                batch.append(self.SpawnActor(blueprint, transform).then(self.SetAutopilot(self.FutureActor, True)))
                self.spawn_points.pop(0)
        
            for response in self.client.apply_batch_sync(batch, self.synchronous_master):
                if response.error:
                    logging.error(response.error)
                else:
                    self.vehicles_list.append(response.actor_id)

            print('Created %d npc vehicles \n' % len(self.vehicles_list))

            # Spawn sensors
            q_list = []
            idx = 0
            
            tick_queue = queue.Queue()
            self.world.on_tick(tick_queue.put)
            q_list.append(tick_queue)
            tick_idx = idx
            idx = idx+1

            # Spawn RGB camera
            # cam_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
            # cam_transform = carla.Transform(carla.Location(88.933, 304.54, 8.327), carla.Rotation(-11.5386, 3.396858, 0))
            cam_transform = carla.Transform(carla.Location(cam_t[0],cam_t[1], cam_t[2]), carla.Rotation(cam_o[0],cam_o[1], cam_o[2]))
            cam_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
            cam_bp.set_attribute('sensor_tick', str(self.tick_sensor))
            cam = self.world.spawn_actor(cam_bp, cam_transform)
            self.nonvehicles_list.append(cam)
            cam_queue = queue.Queue()
            cam.listen(cam_queue.put)
            q_list.append(cam_queue)
            cam_idx = idx
            idx = idx+1
            print('RGB camera ready')

            # Spawn depth camera
            depth_bp = self.world.get_blueprint_library().find('sensor.camera.depth')
            depth_bp.set_attribute('sensor_tick', str(self.tick_sensor))
            depth = self.world.spawn_actor(depth_bp, cam_transform)
            cc_depth_log = carla.ColorConverter.LogarithmicDepth
            self.nonvehicles_list.append(depth)
            depth_queue = queue.Queue()
            depth.listen(depth_queue.put)
            q_list.append(depth_queue)
            depth_idx = idx
            idx = idx+1
            print('Depth camera ready')

            # Spawn segmentation camera
            if self.save_segm:
                segm_bp = self.world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
                segm_bp.set_attribute('sensor_tick', str(self.tick_sensor))
                segm_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
                segm = self.world.spawn_actor(segm_bp, segm_transform)
                cc_segm = carla.ColorConverter.CityScapesPalette
                self.nonvehicles_list.append(segm)
                segm_queue = queue.Queue()
                segm.listen(segm_queue.put)
                q_list.append(segm_queue)
                segm_idx = idx
                idx = idx+1
                print('Segmentation camera ready')

            # Spawn LIDAR sensor
            if self.save_lidar:
                lidar_bp = self.world.get_blueprint_library().find('sensor.lidar.ray_cast')
                lidar_bp.set_attribute('sensor_tick', str(self.tick_sensor))
                lidar_bp.set_attribute('channels', '64')
                lidar_bp.set_attribute('points_per_second', '1120000')
                lidar_bp.set_attribute('upper_fov', '30')
                lidar_bp.set_attribute('range', '100')
                lidar_bp.set_attribute('rotation_frequency', '20')
                lidar_transform = carla.Transform(carla.Location(x=0, z=4.0))
                lidar = self.world.spawn_actor(lidar_bp, lidar_transform)
                self.nonvehicles_list.append(lidar)
                lidar_queue = queue.Queue()
                lidar.listen(lidar_queue.put)
                q_list.append(lidar_queue)
                lidar_idx = idx
                idx = idx+1
                print('LIDAR ready')

            weathers = [carla.WeatherParameters.ClearNoon, \
                        carla.WeatherParameters.CloudyNoon, \
                        carla.WeatherParameters.WetNoon, \
                        carla.WeatherParameters.WetCloudyNoon, \
                        carla.WeatherParameters.MidRainyNoon, \
                        carla.WeatherParameters.HardRainNoon, \
                        carla.WeatherParameters.SoftRainNoon, \
                        carla.WeatherParameters.ClearSunset, \
                        carla.WeatherParameters.CloudySunset, \
                        carla.WeatherParameters.WetSunset, \
                        carla.WeatherParameters.WetCloudySunset, \
                        carla.WeatherParameters.MidRainSunset, \
                        carla.WeatherParameters.HardRainSunset, \
                        carla.WeatherParameters.SoftRainSunset]
            time_sim = 0
            for weather in tqdm(weathers):
                self.world.set_weather(weather)
                print(f'Current weather is {self.world.get_weather()}')
                # Begin the loop
                # time_sim = 0
                img_idx = 0
                
                while img_idx < num_images:
                    # Extract the available data
                    nowFrame = self.world.tick()

                    # Check whether it's time to capture data
                    if time_sim >= self.tick_sensor:
                        img_idx = img_idx + 1
                        data = [retrieve_data(q,nowFrame) for q in q_list]
                        assert all(x.frame == nowFrame for x in data if x is not None)

                        # Skip if any sensor data is not available
                        if None in data:
                            continue
                        
                        vehicles_raw = self.world.get_actors().filter('vehicle.*')
                        snap = data[tick_idx]
                        rgb_img = data[cam_idx]
                        depth_img = data[depth_idx]
                        
                        # Attach additional information to the snapshot
                        vehicles = cva.snap_processing(vehicles_raw, snap)

                        # Save depth image, RGB image, and Bounding Boxes data
                        if self.save_depth:
                            depth_img.save_to_disk('out_depth/%06d.png' % depth_img.frame, cc_depth_log)
                        depth_meter = cva.extract_depth(depth_img)
                        filtered, removed =  cva.auto_annotate(vehicles, cam, depth_meter, json_path='vehicle_class_json_file.txt')

                        # print(filtered['3dbbox'])
                        # print(filtered['vehicles'])
                        # filtered_vehicles = filtered['vehicles']
                        # for vehicle in filtered_vehicles:
                        #     bb_cords = cva.create_bb_points(vehicle)

                        
                        if is_in_darknet:
                            cva.save2darknet(filtered['bbox'], filtered['class'], rgb_img)
                        else:
                            cva.save_output(rgb_img, filtered['bbox'], filtered['class'], removed['bbox'], removed['class'], save_patched=True, out_format='json')
                        
                        # save 3d bbox
                        np.save("data/obj/"+'%06d_3d.npy' % rgb_img.frame, filtered['3dbbox'])
                        np.save("data/obj/"+'%06d_id.npy' % rgb_img.frame, filtered['id'])

                        
                        # Save segmentation image
                        if self.save_segm:
                            segm_img = data[segm_idx]
                            segm_img.save_to_disk('out_segm/%06d.png' % segm_img.frame, cc_segm)

                        # Save LIDAR data
                        if self.save_lidar:
                            lidar_data = data[lidar_idx]
                            lidar_data.save_to_disk('out_lidar/%06d.ply' % segm_img.frame)
                        
                        time_sim = 0
                    time_sim = time_sim + self.settings.fixed_delta_seconds
                
            
        finally:
            cva.save2darknet(None,None,None,save_train=True)
            try:
                cam.stop()
                depth.stop()
                if self.save_segm:
                    segm.stop()
                if self.save_lidar:
                    lidar.stop()
            except:
                print("Simulation ended before sensors have been created")
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            self.world.apply_settings(settings)

            print('\ndestroying %d vehicles' % len(self.vehicles_list))
            self.client.apply_batch([carla.command.DestroyActor(x) for x in self.vehicles_list])

            print('destroying %d nonvehicles' % len(self.nonvehicles_list))
            self.client.apply_batch([carla.command.DestroyActor(x) for x in self.nonvehicles_list])

            time.sleep(0.5)

    
