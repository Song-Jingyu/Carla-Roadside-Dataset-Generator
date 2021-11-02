from dataset_generator import dataset_generator
import carla

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
    dg = dataset_generator(50, 'Town02')
    cam_t = [88.933, 304.54, 8.327]
    cam_o = [-11.5386, 3.396858, 0]
    dg.start_simulation(cam_t, cam_o, True, 1000)