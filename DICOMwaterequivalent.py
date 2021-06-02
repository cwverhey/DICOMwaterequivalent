#!/usr/bin/env python3
#
# DICOMwaterequivalent
#
# Calculates water equivalent area (Aw) and water equivalent circle diameter (Dw) for
# CT DICOM images, as proposed by:
#
#     McCollough C, Bakalyar DM, Bostani M, Brady S, Boedeker K, Boone JM, Chen-Mayer HH,
#     Christianson OI, Leng S, Li B, McNitt-Gray MF. Use of water equivalent diameter for
#     calculating patient size and size-specific dose estimates (SSDE) in CT: The Report of
#     AAPM Task Group 220. AAPM report. 2014 Sep;2014:6.
#
# Requirements and Usage: see README.md or https://github.com/cwverhey/DICOMwaterequivalent
#
# Copyright:
# 2018 Caspar Verhey (caspar@verhey.net), MIT License (see LICENSE)
#

import cv2
import numpy as np
import math
import pydicom

def DICOMwaterequivalent(dicom_filename, threshold, window = False):

    # load DICOM image
    dicom_pydicom  = pydicom.read_file(dicom_filename)
    dicom_img = dicom_pydicom.pixel_array # dicom pixel values as 2D numpy pixel array
    dicom_img = dicom_img - 1000.0 # remap scale 0:... to HU -1000:...

    # determine pixel area in mm²/px²
    scale = dicom_pydicom.PixelSpacing[0] * dicom_pydicom.PixelSpacing[1]

    # map ww/wl for contour detection (filter_img)
    remap = lambda t: 255.0 * (1.0 * t - (threshold - 0.5))
    filter_img = np.array([remap(row) for row in dicom_img])
    filter_img = np.clip(filter_img, 0, 255)
    filter_img = filter_img.astype(np.uint8)

    # find contours, without hierarchical relationships
    ret,thresh = cv2.threshold(filter_img, 127, 255, 0)
    # cv2 >= 4.0 has a different output format
    if int(cv2.__version__.split('.')[0]) <= 4:
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    else:
        image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
    # calculate area and equivalent circle diameter for the largest contour (assumed to be the patient without table or clothing)
    roi_contour = max(contours, key=lambda a: cv2.contourArea(a))
    roi_area = cv2.contourArea(roi_contour) * scale
    roi_equiv_circle_diam = 2.0*math.sqrt(roi_area/math.pi)

    hull_contour = cv2.convexHull(roi_contour)
    hull_area = cv2.contourArea(hull_contour) * scale
    hull_equiv_circle_diam = 2.0*math.sqrt(hull_area/math.pi)

    # create mask of largest contour
    mask_img = np.zeros((dicom_img.shape), np.uint8)
    cv2.drawContours(mask_img,[roi_contour],0,255,-1)

    # calculate mean HU of mask area
    roi_mean_hu = cv2.mean(dicom_img, mask=mask_img)[0]

    # calculate water equivalent area (Aw) and water equivalent circle diameter (Dw)
    water_equiv_area = 0.001 * roi_mean_hu * roi_area + roi_area # AAPM 220 formula 3d
    water_equiv_circle_diam = 2.0*math.sqrt(water_equiv_area/math.pi)

    if window:
        # map ww/wl to human-viewable image (view_img)
        remap = lambda t: 255.0 * (1.0 * t - (window[1] - 0.5 * window[0])) / window[0] # create LUT function; window[0]: ww, window[1]: wl
        view_img = np.array([remap(row) for row in dicom_img]) # rescale
        view_img = np.clip(view_img, 0, 255) # limit to 8 bit
        view_img = view_img.astype(np.uint8) # set color depth
        view_img = cv2.cvtColor(view_img, cv2.COLOR_GRAY2RGB) # add RBG channels

        # create overlay to draw on human-viewable image (to be added as transparent layer)
        overlay_img = np.copy(view_img)

        # draw contour 3px wide on overlay layer, merge layers with transparency
        cv2.drawContours(overlay_img, [hull_contour], -1, (0,255,255), 2, cv2.LINE_AA)
        cv2.drawContours(overlay_img, [roi_contour], -1, (0,255,0), 2, cv2.LINE_AA)
        cv2.addWeighted(overlay_img, 0.40, view_img, 1 - 0.40, 0, view_img)
        
        # add text: first draw shade, then draw text over it
        cv2.putText(view_img, "(equiv.) area", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "(equiv.) area", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "equiv. circle diam.", (265,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "equiv. circle diam.", (265,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        
        
        cv2.putText(view_img, "water eq.", (10,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "water eq.", (10,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm  (Aw)".format(water_equiv_area), (100,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm  (Aw)".format(water_equiv_area), (100,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "2", (189,32), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "2", (189,32), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm (Dw)".format(water_equiv_circle_diam), (265,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm (Dw)".format(water_equiv_circle_diam), (265,36), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,200,200), 1, cv2.LINE_AA)
        
        
        cv2.putText(view_img, "ROI", (10,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "ROI", (10,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm".format(roi_area), (100,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm".format(roi_area), (100,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "2", (189,49), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "2", (189,49), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0,255,0), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm".format(roi_equiv_circle_diam), (265,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm".format(roi_equiv_circle_diam), (265,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        
        
        cv2.putText(view_img, "hull", (10,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "hull", (10,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm".format(hull_area), (100,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm".format(hull_area), (100,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "2", (189,65), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "2", (189,65), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0,200,200), 1, cv2.LINE_AA)
        
        cv2.putText(view_img, "{:.0f} mm".format(hull_equiv_circle_diam), (265,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(view_img, "{:.0f} mm".format(hull_equiv_circle_diam), (265,68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,200), 1, cv2.LINE_AA)
        
    else:
        view_img = False

    # return values
    ret = { "roiArea": roi_area,
            "roiEquivalentCircleDiameter": roi_equiv_circle_diam,
            "waterEquivalentArea": water_equiv_area,
            "Aw": water_equiv_area,
            "waterEquivalentCircleDiameter": water_equiv_circle_diam,
            "Dw": water_equiv_circle_diam,
            "hullArea": hull_area,
            "hullEquivalentCircleDiameter": hull_equiv_circle_diam,
            "image": view_img
          }
    return(ret)

if __name__ == "__main__":

    import sys
    try:
        if len(sys.argv) == 3 or len(sys.argv) == 5:
            filename = sys.argv[1]
            threshold = int(sys.argv[2])
            if len(sys.argv) == 5:
                ww = int(sys.argv[3])
                wl = int(sys.argv[4])
            else:
                ww = 1600
                wl = -400
        else:
            raise AttributeError('Wrong number of parameters')
    except:
        raise AttributeError('\n\nUsage:\n$ DICOMwaterequivalent.py [filename] [threshold] [ww] [wl]\n\nWindow width, window level default to 1600, -400. See README.md or https://github.com/cwverhey/DICOMwaterequivalent for details.')
        
    result = DICOMwaterequivalent(filename, threshold, (ww,wl))
    
    # cv2.imwrite('out.png', result[6]) # to write numpy image as file
    
    # print values except image
    for k in result.keys():
        if(k != 'image'):
            print(k+': '+str(result[k]), flush=True)                # results[0:6] = (Aw, Dw, Ap, Dp, Aph, Dph)
            
    # display image in window
    cv2.imshow('DICOMwaterequivalent', result['image'])
    cv2.waitKey(0) # press any key in graphical window to close
    cv2.destroyAllWindows()
