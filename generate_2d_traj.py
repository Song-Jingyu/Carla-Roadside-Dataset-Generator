## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

import torch
import os
import cv2
import numpy as np
from sort import *

from scipy.optimize import least_squares
import scipy.io


mot_tracker = Sort(max_age=5, iou_threshold=0.05) 



model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/jingyu/Downloads/best.pt')  # default
# model = torch.hub.load('ultralytics/yolov5', 'yolov5m', classes=1)
# model.load_state_dict(torch.load('/home/jingyu/Simulation/Carla-Roadside-Dataset-Generator/yolov5/runs/train/exp3/weights/best.pt')['model'].state_dict())

img_dir = '/media/jingyu/Data/Carla_simulation/Carla-Roadside-Dataset-Generator/data/new_setting/'
img_list = []
imgs = sorted(os.listdir(img_dir))
trakced_list = []

# print(imgs)
for img in imgs:
    if os.path.splitext(img)[1] != '.jpg':
        continue
    img_file = img_dir + img
    results = model(img_file)
    # print(results.pred)
    prediction = results.pred[0].cpu().numpy()
    prediction = np.array(prediction, dtype=float)
    # print(prediction)
    track_bbs_ids = mot_tracker.update(prediction[:,:4])
    track_bbs_ids = np.array(track_bbs_ids)
    trakced_list.append(track_bbs_ids)
    img_list.append(os.path.splitext(img)[0])
    # print(track_bbs_ids)

    # print(prediction)
    im = cv2.imread(img_file)
    for i in range(prediction.shape[0]):
        pred = np.array(np.floor(prediction[i]), dtype=int)
        cv2.rectangle(im,(pred[0],pred[1]),(pred[2],pred[3]),(0,255,0),2)

    for i in range(track_bbs_ids.shape[0]):
        cv2.putText(im, f'{int(track_bbs_ids[i,4])}', (int(track_bbs_ids[i,0]),int(track_bbs_ids[i,1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
    cv2.imshow("Show",im)
    cv2.waitKey(50)

cv2.destroyAllWindows()

interested_id_list = [1,9]
interedted_array = []
for interested_id in interested_id_list:
    for i in range(len(trakced_list)):
        current_arr = trakced_list[i]
        interested_where = np.where(current_arr[:,4] == interested_id)

        if len(interested_where[0]) > 0:
            temp = current_arr[interested_where[0],:]
            temp[0,4] = img_list[i]
            interedted_array.append(temp)
    
interedted_array = np.array(interedted_array).reshape(-1,5)
print(interedted_array)
print(interedted_array.shape)
# np.save("bbox_traj", interedted_array)
# scipy.io.savemat('uv.mat', dict(uv=interedted_array))