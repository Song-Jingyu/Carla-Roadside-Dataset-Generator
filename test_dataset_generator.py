## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

from dataset_generator import dataset_generator
import carla

# TODO: change these parameters based on your usage
NUM_OF_VEHICLES = 50 #How many vehicles are used 
NUM_OF_FRAMES = 1000
WORLD = 'Town02'
CAM_T = [88.933, 304.54, 8.327]
CAM_O = [-11.5386, 3.396858, 0]
IS_DARKNET = True

# weathers = [carla.WeatherParameters.ClearNoon, \
#     carla.WeatherParameters.CloudyNoon, \
#     carla.WeatherParameters.WetNoon, \
#     carla.WeatherParameters.WetCloudyNoon, \
#     carla.WeatherParameters.MidRainyNoon, \
#     carla.WeatherParameters.HardRainNoon, \
#     carla.WeatherParameters.SoftRainNoon, \
#     carla.WeatherParameters.ClearSunset, \
#     carla.WeatherParameters.CloudySunset, \
#     carla.WeatherParameters.WetSunset, \
#     carla.WeatherParameters.WetCloudySunset, \
#     carla.WeatherParameters.MidRainSunset, \
#     carla.WeatherParameters.HardRainSunset, \
#     carla.WeatherParameters.SoftRainSunset]

if __name__ == "__main__":
    dg = dataset_generator(NUM_OF_VEHICLES, WORLD)
    
    dg.start_simulation(CAM_T, CAM_O, IS_DARKNET, NUM_OF_FRAMES)