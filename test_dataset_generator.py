## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

from dataset_generator import dataset_generator
import carla

# TODO: change these parameters based on your usage
NUM_OF_VEHICLES = 30 #How many vehicles are used 
NUM_OF_FRAMES = 1000
WORLD = 'Town02'
# CAM_T = [88.933, 304.54, 8.327]
# CAM_O = [-11.5386, 3.396858, 0]

# Transform(Location(x=139.644974, y=303.487366, z=9.632331), Rotation(pitch=-13.819795, yaw=-175.325409, roll=0.000111))
# CAM_T = [139.645, 303.487, 9.632]
# CAM_O = [-13.82, -175.3254, 0]

# Transform(Location(x=108.859444, y=243.846329, z=9.039239), Rotation(pitch=-7.108888, yaw=-24.839268, roll=0.000170))
CAM_T = [108.86, 243.85,9.04]
CAM_O = [-7.109, -24.84, 0]
IS_DARKNET = True
TICK_SENSOR = 0.3

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
    dg = dataset_generator(NUM_OF_VEHICLES, WORLD, TICK_SENSOR)
    
    dg.start_simulation(CAM_T, CAM_O, IS_DARKNET, NUM_OF_FRAMES)