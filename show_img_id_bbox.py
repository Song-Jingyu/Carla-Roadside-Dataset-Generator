## Maintainer: Jingyu Song #####
## Contact: jingyuso@umich.edu #####

import cv2
import os
import numpy as np


img_dir = '/Volumes/Jingyu-SSD/Simulation/new_setting/'

imgs = sorted(os.listdir(img_dir))
img_height = 600
img_width = 800

for img in imgs:
    if img.split('.')[1] != 'jpg':
        continue
    img_file = img_dir + img
    img_seq = img.split('.')[0]
    bbox = np.loadtxt(img_dir + img_seq + '.txt')
    id = np.load(img_dir + img_seq + '_id.npy')
    

    # print(prediction)
    im = cv2.imread(img_file)
    bbox = np.reshape(bbox, (-1,5))
    for i in range(bbox.shape[0]):
        # [[0.         0.32027825 0.58996172 0.08021529 0.05008581]
        # [0.         0.23996279 0.5520495  0.06284257 0.03594672]]
        
        x1 = (bbox[i,1] - 0.5*bbox[i,3]) * img_width
        x2 = (bbox[i,1] + 0.5*bbox[i,3]) * img_width
        y1 = (bbox[i,2] - 0.5*bbox[i,4]) * img_height
        y2 = (bbox[i,2] + 0.5*bbox[i,4]) * img_height
        # pred = np.array(np.floor(prediction[i]), dtype=int)
        cv2.rectangle(im,(int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),2)

        org = (int(bbox[i,1]*img_width),int(bbox[i,2]*img_height))

        font = cv2.FONT_HERSHEY_SIMPLEX

        fontScale = 1
        # Blue color in BGR
        color = (255, 0, 0)
        
        # Line thickness of 2 px
        thickness = 2
        
        # Using cv2.putText() method
        im = cv2.putText(im, f'{id[i]}', org, font, 
                        fontScale, color, thickness, cv2.LINE_AA)
    # for i in range(track_bbs_ids.shape[0]):
    
        # cv2.putText(im, f'{int(track_bbs_ids[i,4])}', (int(track_bbs_ids[i,0]),int(track_bbs_ids[i,1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
        cv2.imshow("Show",im)
        cv2.waitKey(20)

cv2.destroyAllWindows()