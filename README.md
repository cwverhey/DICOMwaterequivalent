# DICOMwaterequivalent
Python script to calculate water equivalent area (Aw) and water equivalent circle diameter (Dw) for 16 bit CT DICOM images, as proposed by AAPM Task Group 220 for calculating patient size for size-specific dose estimates (SSDE) in CT. Can be used as a standalone script or included as a function.

## Requirements
cv2, numpy, pydicom

    $ pip3 install opencv-python numpy pydicom

## Python function
### Usage

    >>> import DICOMwaterequivalent
    >>> DICOMwaterequivalent(filename, threshold, window)

* filename:  DICOM file,
* threshold: ROI contour threshold level,
* window:    Optional, view window for output image, as tuple (ww,wl). No image will be outputted if omitted.

### Returns
Tuple containing:
1.  water equivalent area (Aw) in mm² (float),
2.  water equivalent diameter (Dw) in mm (float),
3.  ROI area in mm² (float),
4.  ROI equivalent circle diameter in mm (a circle with ROI area) (float),
5.  ROI hull area in mm² (float),
6.  ROI hull equivalent circle diameter in mm (float),
7.  result image displaying ROI and ROI hull contours (numpy array).

### Example

    >>> import DICOMwaterequivalent
    >>> equiv = DICOMwaterequivalent('in.dcm', -350, (1000,40))
    >>> print(equiv)
    ( 24740.231323242188, 
      177.48307205659782, 
      27518.49097592727,
      187.18341518945613,
      25731.055450439453,
      181.0022025481258,
      array([[[0, 0, 0], ... ]]], dtype=uint8))
    )
    >>> cv2.imwrite('out.png', equiv[6])

## Standalone use
### Usage

    ./DICOMwaterequivalent.py <filename> <threshold>

* filename:  DICOM file
* threshold: ROI contour threshold level

### Output
##### console
```
(
	water equivalent area (Aw) in mm² (float),
	water equivalent diameter (Dw) in mm (float),
	ROI area in mm² (float),
	ROI equivalent circle diameter in mm (a circle with ROI area) (float),
	ROI hull area in mm² (float),
	ROI hull equivalent circle diameter in mm (float)
)
```

##### graphical
result image displaying ROI and ROI hull contours

### Example

    $ ./DICOMwaterequivalent.py image-1001.dcm -250
    (24740.231323242188, 177.48307205659782, 27518.49097592727, 187.18341518945613, 25731.055450439453, 181.0022025481258)
<img align="left" src="screenshot.png" />
<br clear="all" />
* Example source image courtesy of Patient Contributed Image Repository patient 54879843, available from http://www.pcir.org/researchers/downloads_available.html
