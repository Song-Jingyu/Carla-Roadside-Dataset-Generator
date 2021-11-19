#!/usr/bin/env python

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('./PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================

# Transform(Location(x=108.859444, y=243.846329, z=9.039239), Rotation(pitch=-7.108888, yaw=-24.839268, roll=0.000170))

# Transform(Location(x=139.268784, y=241.208359, z=7.610488), Rotation(pitch=-18.796810, yaw=-138.667511, roll=0.000178))

# Transform(Location(x=137.371368, y=243.293045, z=6.444705), Rotation(pitch=-18.272455, yaw=-134.825333, roll=0.000058))


import carla

_HOST_ = '127.0.0.1'
_PORT_ = 2000
_SLEEP_TIME_ = 1


def main():

	client = carla.Client(_HOST_, _PORT_)
	print(client.get_available_maps())

	client.set_timeout(2.0)
	world = client.load_world('Town02')

	
	# print(help(t))
	# print("(x,y,z) = ({},{},{})".format(t.location.x, t.location.y,t.location.z))
	

	while(True):
		t = world.get_spectator().get_transform()
		# coordinate_str = "(x,y) = ({},{})".format(t.location.x, t.location.y)
		coordinate_str = "(x,y,z) = ({},{},{})".format(t.location.x, t.location.y,t.location.z)
		print(t)
        
		time.sleep(_SLEEP_TIME_)



if __name__ == '__main__':
	main()