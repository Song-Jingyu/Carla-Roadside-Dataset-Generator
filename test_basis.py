## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

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

def main():
    args = parser()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_id_list = []
    sensor_list = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False

    try:
        world = client.load_world('Town02')


        origin_settings = world.get_settings()
        traffic_manager = client.get_trafficmanager(args.tm_port)
        # every vehicle keeps a distance of 3.0 meter
        traffic_manager.set_global_distance_to_leading_vehicle(3.0)
        # Set physical mode only for cars around ego vehicle to save computation
        traffic_manager.set_synchronous_mode(True)
        # default speed is 30
        traffic_manager.global_percentage_speed_difference(-50)
        blueprints_vehicle = world.get_blueprint_library().filter("vehicle.*")
        print(blueprints_vehicle)
        print(len(blueprints_vehicle))

        spawn_points = world.get_map().get_spawn_points()
        # print(len(spawn_points))

        print(client.get_available_maps())

        

        


        


    
    finally:
        # world.apply_settings(origin_settings)
        # print('\ndestroying %d vehicles' % len(vehicles_id_list))

        # client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_id_list])
        # for sensor in sensor_list:
        #     sensor.destroy()
        print('done.')

    print("main")

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')
