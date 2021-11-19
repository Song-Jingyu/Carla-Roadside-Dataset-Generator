## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

import numpy as np
import scipy.io

traj = np.load("bbox_traj.npy")
print(traj.shape)
scipy.io.savemat('test.mat', dict(traj=traj))
