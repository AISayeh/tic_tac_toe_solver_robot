from __future__ import print_function
import sys
from enum import Enum
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2 as cv
import math

global_med = 0
class Return_mode(Enum):
    list = 1
    string = 2
    list2d = 3

def reject_outliers(data):
    global global_med
    med = np.median(data)
    global_med = med
    maskMin = med * 0.7
    maskMax = med * 1.2
    print('med = %s' % str(int(med)))
    print('min = %s' % str(int(maskMin)))
    print('max = %s' % str(int(maskMax)))
    mask = np.ma.masked_outside(data, maskMin, maskMax)
    return mask

def PolygonArea(corners):
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def center_of_points(points):
    center_x = 0
    center_y = 0
    for (x,y) in points:
        center_x += x / float(len(points))
        center_y += y / float(len(points))
    return (center_x, center_y)

def distance(p1,p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

def removeRedundency(polygs):
    i = 0
    while(i < len(polygs)):
        j = i + 1
        mid = center_of_points(polygs[i])
        while (j < len(polygs)):
            flag = False
            maxDist = math.sqrt(global_med) // 4
            cj = center_of_points(polygs[j])
            dist = distance(mid, cj)
            if dist < maxDist:
                flag = True
                polygs.pop(j)
            if not flag:
                j += 1
        i += 1
    return polygs

def find_squares(img):
    img = cv.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv.Canny(gray, 0, 50, apertureSize=5)
                bin = cv.dilate(bin, None)
            else:
                _retval, bin = cv.threshold(gray, thrs, 255, cv.THRESH_BINARY)
            im2, contours, _hierarchy = cv.findContours(bin, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv.arcLength(cnt, True)
                cnt = cv.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv.contourArea(cnt) > 1000 and cv.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
    return squares

def crop(img, square):
    minX = square[0][0]
    minY = square[0][1]
    maxX = square[0][0]
    maxY = square[0][1]
    for p in square:
        if p[0] < minX:
            minX = p[0]
        if p[0] > maxX:
            maxX = p[0]
        if p[1] < minY:
            minY = p[1]
        if p[1] > maxY:
            maxY = p[1]
    minX += 10
    minY += 10
    maxX -= 10
    maxY -= 10
    return img[minY: maxY , minX: maxX]

def square_middle(sqr):
    x_min = sqr[0][0]
    x_max = sqr[0][0]
    y_min = sqr[0][1]
    y_max = sqr[0][1]

    for i in sqr:
        if i[0] < x_min:
            x_min = i[0]
        if i[0] > x_max:
            x_max = i[0]
        if i[1] < y_min:
            y_min = i[1]
        if i[1] > y_max:
            y_max = i[1]

    return ((x_min + x_max) // 2, (y_min + y_max) // 2)

def main(path):
    from glob import glob
    for fn in glob(path):
        img = cv.imread(fn,0)
        squares = find_squares(img)
        areas = []
        for i in squares:
            a = PolygonArea(i)
            areas.append(int(a))

        masked_areas = list(reject_outliers(areas))
        idx = 0
        for ar in masked_areas:
            if str(ar) == '--':
                squares.pop(idx)
                idx-=1
            idx+=1
        squares = sorted(squares, key=lambda a: PolygonArea(a), reverse=True)
        squares = removeRedundency(squares)

        if len(squares) != 9:
            print("can't extract this image try another one")
            continue
        mids = []
        for s in squares:
            mids.append((square_middle(s), s))

        mids = sorted(mids, key=lambda a: a[0][1], reverse=False)
        r1 = mids[0:3]
        r1 = sorted(r1, key=lambda a: a[0][0], reverse=False)
        r2 = mids[3:6]
        r2 = sorted(r2, key=lambda a: a[0][0], reverse=False)
        r3 = mids[6:9]
        r3 = sorted(r3, key=lambda a: a[0][0], reverse=False)
        sqs = [r1,r2,r3]
        status = ""
        for k in sqs:
            for s in k:
                cell = crop(img,s[1])
                retr, thresh = cv.threshold(cell, 70, 255, 0)
                im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_TC89_L1)
                cv.drawContours(cell, contours, -1, (0, 255, 0), 2)
                largecont = []
                for c in contours:
                    peri = cv.arcLength(c, True)
                    approx = cv.approxPolyDP(c, 0.02 * peri, True)
                    if len(approx) >= 8:
                        largecont.append(len(approx))

                if len(largecont) == 1:
                    status += "X"
                elif len(largecont) > 1:
                    status += "O"
                else:
                    status += "-"

        return status

    print('Done')


def detect_board(path, return_mode = Return_mode.list):
    img = cv.imread(path,0)
    return main(path)
