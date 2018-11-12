import cv2
import numpy as np
import os,sys

def calculateSizes(frameSize, scaleGrid, scaleSpace,distance):
    width = int((scaleGrid*frameSize[0]))
    height = int((scaleGrid*frameSize[1]))
    
    gridSize = max((width,height))
    size=gridSize*scaleSpace+distance
    return width,height, size

def makeHologram(frame,sizes):
    '''
        Create 3D hologram from image (must have equal dimensions)
    '''
    
    image = cv2.resize(frame, (sizes[0], sizes[1]), interpolation = cv2.INTER_CUBIC)
    
    up = image.copy()
    down = rotate_bound(image.copy(),180)
    right = rotate_bound(image.copy(), 90)
    left = rotate_bound(image.copy(), 270)
    
    hologram = np.zeros([sizes[2],sizes[2],3], image.dtype)
    center_x = int((hologram.shape[0])/2)
    center_y = int((hologram.shape[1])/2)

    vert_x = (up.shape[0])/2
    vert_y = (up.shape[1])/2
    hologram[:up.shape[0], int(center_x-vert_x):int(center_x+vert_x)] = up
    hologram[ int(hologram.shape[1]-down.shape[1]):int(hologram.shape[1]) , int(center_x-vert_x):int(center_x+vert_x)] = down
    hori_x = (right.shape[0])/2
    hori_y = (right.shape[1])/2
    hologram[ int(center_x-hori_x) : int(center_x+hori_x) , int(hologram.shape[1]-right.shape[1]) : int(hologram.shape[1])] = right
    hologram[ int(center_x-hori_x) : int(center_x-hori_x+left.shape[0]) ,  : int(left.shape[1]) ] = left

    return hologram

def process_video(video):
    cap = cv2.VideoCapture(video)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    ret = True
    
    size = (640,640)
    sizes=calculateSizes(size,0.5,4,0)
    
    out = cv2.VideoWriter('hologram.avi',fourcc, 30.0, (sizes[2],sizes[2]))
    while(ret):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, size, interpolation = cv2.INTER_CUBIC)
            holo = makeHologram(frame, sizes)
            out.write(holo)
        
    
    # Release everything if job is finished
    cap.release()
    out.release()
    return

def rotate_bound(image, angle):

    h=image.shape[0]
    w=image.shape[1]
    (cX, cY) = (w // 2, h // 2)
 
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
 
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
 
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
 
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))
    


process_video("video.mp4")
