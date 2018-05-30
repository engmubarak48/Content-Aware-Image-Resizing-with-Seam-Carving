# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 19:26:42 2018

@author: JAMA HUSEIN MOHAMUD
"""

import cv2
import numpy as np

image = cv2.imread("Baseball.jpg")

def energy(image):
    blur = cv2.GaussianBlur(image, (3, 3), 0, 0)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    ENERGY = cv2.add(np.absolute(sobelx), np.absolute(sobely))    
    return ENERGY 
 
def CEV(energy):
    height, width = energy.shape[:2]
    comul_energy = np.zeros((height, width))

    for i in range(1, height):
        for j in range(width):
            left = comul_energy[i - 1, j - 1] if j - 1 >= 0 else 1e6
            middle = comul_energy[i - 1, j]
            right = comul_energy[i - 1, j + 1] if j + 1 < width else 1e6
            
            comul_energy[i, j] = energy[i, j] + min(left, middle, right)

    return comul_energy

def CEH(energy):
    height, width = energy.shape[:2]
    comul_energy = np.zeros((height, width))

    for j in range(1, width):
        for i in range(height):
            top = comul_energy[i - 1, j - 1] if i - 1 >= 0 else 1e6
            middle = comul_energy[i, j - 1]
            bottom = comul_energy[i + 1, j - 1] if i + 1 < height else 1e6

            comul_energy[i, j] = energy[i, j] + min(top, middle, bottom)

    return comul_energy

def horizontal_seam(comul_energy):
    height, width = comul_energy.shape[:2]
    previous = 0
    seam = []
    for i in range(width - 1, -1, -1):
        col = comul_energy[:, i]

        if i == width - 1:
            previous = np.argmin(col)

        else:
            top = col[previous - 1] if previous - 1 >= 0 else 1e6
            middle = col[previous]
            bottom = col[previous + 1] if previous + 1 < height else 1e6

            previous = previous + np.argmin([top, middle, bottom]) - 1

        seam.append([i, previous])

    return seam

def vertical_seam(comul_energy):
    height, width = comul_energy.shape[:2]
    previous = 0
    seam = []
    for i in range(height - 1, -1, -1):
        row = comul_energy[i, :]

        if i == height - 1:
            previous = np.argmin(row)
            seam.append([previous, i])
        else:
            left = row[previous - 1] if previous - 1 >= 0 else 1e6
            middle = row[previous]
            right = row[previous + 1] if previous + 1 < width else 1e6

            previous = previous + np.argmin([left, middle, right]) - 1
            seam.append([previous, i])

    return seam

def seam_drawing(image, seam):
    cv2.polylines(image, np.int32([np.asarray(seam)]), False, (0, 255, 0))
    cv2.imshow('seam', image)
    cv2.imshow('seam', image)
    cv2.waitKey(1)
    
def RHS(image, seam):
    height, width, bands = image.shape
    removed = np.zeros((height - 1, width, bands), np.uint8)

    for x, y in reversed(seam):
        removed[0:y, x] = image[0:y, x]
        removed[y:height - 1, x] = image[y + 1:height, x]

    return removed

def RVS(image, seam):
    height, width, bands = image.shape
    removed = np.zeros((height, width - 1, bands), np.uint8)

    for x, y in reversed(seam):
        removed[y, 0:x] = image[y, 0:x]
        removed[y, x:width - 1] = image[y, x + 1:width]

    return removed

def seam_carving(image, width , height):
    result = image

    img_height, img_width = image.shape[:2]
    dy = img_height - height if img_height - height > 0 else 0
    dx = img_width - width if img_width - width > 0 else 0

    for i in range(dy):
        comul_energy = CEH(energy(result))
        seam = horizontal_seam(comul_energy)
        seam_drawing(result, seam)
        result = RHS(result, seam)

    for i in range(dx):
        comul_energy = CEV(energy(result))
        seam = vertical_seam(comul_energy)
        seam_drawing(result, seam)
        result = RVS(result, seam)

    print ('all seams are removed, press any button to close window.')

    cv2.imshow('seam', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# Uncomment the following four lines if you want to show the energy image
#print('press any button seam carve the image')
#cv2.imshow('Energy image', energy(image))
#cv2.waitKey(0)
#cv2.destroyAllWindows()
print('please input the dimentions that you want to resize to')
width = input('please input the width: ')
height = input('please input the height: ')
print('========================watch the result===========================')
CARVED = seam_carving(image, int(width), int(height))