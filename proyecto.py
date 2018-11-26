import cv2
import numpy as np
import os,sys
import argparse
import re

parser = argparse.ArgumentParser()

# Define flags
parser.add_argument('-i', '--video_in', dest='video_in', help='Path to video in mp4, avi or wmv format')
parser.add_argument('-o', '--video_output', dest='video_output', help='Path to video')
parser.add_argument('-s', '--size', dest='size', type=int, help='Resolution for video output')


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


def process_video(video_in, video_out, size_dim):
    cap = cv2.VideoCapture(video_in)

    width = cap.get(3)
    height = cap.get(4)
    print('\nVideo in dimensions: ')
    print('width:', width)
    print('height:', height)

    maxi = int(max((width, height)))
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    ret = True
    dim = size_dim//3

    print('\nVideo output dimensions: ')
    print('Width, height: ', size_dim)
    size = (dim, dim)
    sizes=calculateSizes(size,1,3,0)
    
    out = cv2.VideoWriter(video_out, fourcc, 30.0, (sizes[2],sizes[2]))
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

# process_video("video1.avi")

args = parser.parse_args()

def validate_output_name(video_out):
    reg = r'^\w*\.(mp4|avi|wmv)$'
    return True if re.match(reg, video_out) else False


def validate_flags(video_in, video_out, size):

    if video_in == None or video_out == None or size == None:
        return False
    else:
        try:
            if os.path.isfile(video_in):
                if validate_output_name(video_out):
                    return True
                else:
                    print('Output video name error')
                    return False
            else:
                print('File doesn\'t exists')
                return False
        except ValueError:
            print('Error reading file')
            return False


if validate_flags(args.video_in, args.video_output, args.size):
    video_in = args.video_in
    video_out = args.video_output
    size = args.size
    
    process_video(video_in, video_out, size)
