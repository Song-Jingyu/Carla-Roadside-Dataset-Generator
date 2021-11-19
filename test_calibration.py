## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

from numpy.lib.function_base import append
from scipy.optimize.nonlin import Jacobian
# import torch
import os
import cv2
import numpy as np
from sort import *

from scipy.optimize import least_squares
import scipy.io


import scipy.io


mot_tracker = Sort() 



# model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/jingyu/Simulation/Carla-Roadside-Dataset-Generator/yolov5/runs/train/exp3/weights/best.pt')  # default
# model = torch.hub.load('ultralytics/yolov5', 'yolov5m', classes=1)
# model.load_state_dict(torch.load('/home/jingyu/Simulation/Carla-Roadside-Dataset-Generator/yolov5/runs/train/exp3/weights/best.pt')['model'].state_dict())


img_dir = '/media/jingyu/Data/Carla_simulation/Carla-Roadside-Dataset-Generator/data/new_setting'
imgs = sorted(os.listdir(img_dir))
img_list = []
for x in imgs:
    if x.split('.')[1] == 'jpg':
        img_list.append(x.split('.')[0])

print(img_list)
trakced_list = []

list_3d = []
list_2d = []
list_id = []
for img in img_list:
    list_2d.append(np.loadtxt(img_dir+img+'.txt'))
    list_3d.append(np.load(img_dir+img+'_3d.npy'))
    list_id.append(np.load(img_dir+img+'_id.npy'))

# print(list_id)
# print(list_2d[0])

xyz_list = []
uv_list = []
tracking_id = 177

for idx, ids in enumerate(list_id):

    tracking_idx = np.where(ids == tracking_id)
    if len(tracking_idx[0]) == 0:
        print(idx)
    if len(tracking_idx[0]) > 0:
        temp_2d = list_2d[idx].reshape(-1,5)
        temp_2d = temp_2d[ [0],:]
        uv_list.append([temp_2d[0, 1] * 800, temp_2d[0, 2] * 600])

        xyz = list_3d[idx][tracking_idx[0],:,:]
        xyz = xyz.reshape(xyz.shape[1], xyz.shape[2])
        xyz = xyz[:3,:]
        xyz = np.mean(xyz, axis=1)
        xyz_list.append(xyz)
xyz_list = np.array(xyz_list)
print(xyz_list.shape)

uv_list = np.array(uv_list).reshape(-1,2)
print(uv_list.shape)
scipy.io.savemat('xyz.mat', dict(xyz=xyz_list))
scipy.io.savemat('uv.mat', dict(uv=uv_list))


# print(imgs)
# for img in imgs:
#     img = img_dir + img
#     results = model(img)
#     # print(results.pred)
#     prediction = results.pred[0].cpu().numpy()
#     prediction = np.array(prediction, dtype=float)
#     # print(prediction)
#     track_bbs_ids = mot_tracker.update(prediction[:,:4])
#     track_bbs_ids = np.array(track_bbs_ids)
#     trakced_list.append(track_bbs_ids)
#     # print(track_bbs_ids)

#     # print(prediction)
#     im = cv2.imread(img)
#     for i in range(prediction.shape[0]):
#         pred = np.array(np.floor(prediction[i]), dtype=int)
#         cv2.rectangle(im,(pred[0],pred[1]),(pred[2],pred[3]),(0,255,0),2)

#     for i in range(track_bbs_ids.shape[0]):
#         cv2.putText(im, f'{int(track_bbs_ids[i,4])}', (int(track_bbs_ids[i,0]),int(track_bbs_ids[i,1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
#     cv2.imshow("Show",im)
#     cv2.waitKey(30)

# cv2.destroyAllWindows()

# interested_id = 8
# interedted_array = []
# for i in range(len(trakced_list)):
#     current_arr = trakced_list[i]
#     interested_where = np.where(current_arr[:,4] == interested_id)
#     # print(interested_where[0])
#     if len(interested_where[0]) > 0:
#         interedted_array.append(current_arr[interested_where[0],:])
    
interedted_array = np.array(interedted_array).reshape(-1,5)
print(interedted_array)
print(interedted_array.shape)
np.save("bbox_traj", interedted_array)
scipy.io.savemat('uv.mat', dict(uv=interedted_array))
