# DICOMwaterequivalent
This is a python 3 script / program to calculate the patient's water equivalent area (A<sub>w</sub>), water equivalent circle diameter (D<sub>w</sub>), and area-equivalent circle diameter, from 16 bit CT DICOM images. A<sub>w</sub> and D<sub>w</sub> consider tissue attenuation for calculating the patient size for size-specific dose estimates (SSDE) in CT, as proposed by AAPM Task Groups 204 and 220.

The program automatically determines the ROI, as the largest region of tissue above a manually chosen density threshold (in HU) and all tissue enclosed by it.

This script can be used as a [Python function](#python-function) or as a [standalone Python script](#standalone). It returns the following information:

- ROI area: area of the automatically detected ROI, in mm².
- ROI-equivalent-circle diameter: diameter of the circle with the same area as the ROI, in mm.
- water-equivalent area (A<sub>w</sub>): ROI area normalised by its density to the density of water, in mm².
- water-equivalent-circle diameter (D<sub>w</sub>): diameter of the circle with the same area as A<sub>w</sub>, in mm.
- hull area: area of the convex hull around the ROI, in mm².
- hull-equivalent-circle diameter: diameter of the circle with the same area as the hull, in mm.
- image: the input DICOM file, overlaid with contours of the ROI and hull area, and all above measurements.

> :warning: Always check the output image for correct ROI placement. The ROI is automatically placed around the largest contour with HUs above the ROI HU threshold. You must manually set the ROI HU threshold. Confirm that the patient contour is inside the displayed ROI outline, and that the ROI does not include the CT examination table, clothing, implants, ECG leads etc. For measurements other than A<sub>w</sub> and D<sub>w</sub>, also avoid including air. Exclusion of implants is not (yet) possible with this script.

> :warning: This software and its results should not be used blindly without adequate professional judgment. Verify that the pixel-to-mm scaling is done correctly by checking the ROI area with the CT manufacturer's software. Read LICENSE for further disclaimers.

## Contents
  * [Requirements](#requirements)
  * [Standalone](#standalone)
  * [Python function](#python-function)
  * [More information](#more-information)
    + [Using SSDE factors](#using-ssde-factors)
    + [Sources / suggested reading](#sources--suggested-reading)
    + [Contact](#contact)

## Requirements
Modules `cv2` and `pydicom`:

    $ pip3 install opencv-python pydicom

Download the file `DICOMwaterequivalent.py` and place it in your working directory. Alternatively, you can put it in one of the other directories that Python checks for modules. To list these directories: `$ python3 -c 'import sys; print(sys.path)'`

On Linux and MacOS, you might need to make it executable:

	$ chmod +x DICOMwaterequivalent.py

## Standalone
You can call DICOMwaterequivalent.py from the command line:

### Input

    $ ./DICOMwaterequivalent.py <filename> <threshold> <ww> <wl>

* filename:  DICOM file (absolute or relative path).
* threshold: ROI contour threshold level (in HU).
* ww: (optional) window width (default: 1600).
* wl: (optional) window level (default: -400).

You need to specify both ww and wl, or neither.

### Output
* Console: output values (float)
* GUI: image with ROI and hull contours, overlaid with output values (int)

### Example

	$ ./DICOMwaterequivalent.py 480.0.dcm -250
	roiArea: 21445.37160223951
	roiEquivalentCircleDiameter: 165.24253440174482
	waterEquivalentArea: 26328.33432149283
	Aw: 26328.33432149283
	waterEquivalentCircleDiameter: 183.0908965654292
	Dw: 183.0908965654292
	hullArea: 23966.764703619567
	hullEquivalentCircleDiameter: 174.68666972614523
	Press any key in the GUI to quit

<img align="left" src="screenshot.png" />
<br clear="all" />
* Example dicom file courtesy of Patient Contributed Image Repository patient 54879843, available from http://www.pcir.org/researchers/downloads_available.html

## Python function
You can call DICOMwaterequivalent() from your own python script:

### Input

```python
$ python3
>>> from DICOMwaterequivalent import DICOMwaterequivalent
>>> DICOMwaterequivalent(filename, threshold, window)
```

* filename:  DICOM file (absolute or relative path).
* threshold: ROI contour threshold level (in HU).
* window:    (optional) view window for output image, as tuple (ww,wl). If omitted, no image will be outputted.

### Returns
Dictionary containing numerical values as float, image as numpy array.

### Example

```python
$ python3
>>> from DICOMwaterequivalent import DICOMwaterequivalent
>>> equiv = DICOMwaterequivalent('480.0.dcm', -250, (1000,40))
>>> print(equiv)
{'roiArea': 21445.37160223951, 'roiEquivalentCircleDiameter': 165.24253440174482, 'waterEquivalentArea': 26328.33432149283, 'Aw': 26328.33432149283, 'waterEquivalentCircleDiameter': 183.0908965654292, 'Dw': 183.0908965654292, 'hullArea': 23966.764703619567, 'hullEquivalentCircleDiameter': 174.68666972614523, 'image': array([[[0, 0, 0], ... ]]], dtype=uint8)}
>>> import cv2
>>> cv2.imwrite('out.png', equiv['image'])
```

## More information

### Using SSDE factors
SSDE conversion factors can be calculated from _D<sub>w</sub>_ depending on the phantom used for CTDI<sub>vol</sub> estimation. The following formulae are for _D<sub>w</sub>_ in mm:

> For 32 cm phantoms:
> 
>     conversion factor = 3.704369 * e^(-0.003671937*Dw)
>
> For 16 cm phantoms:
> 
>     conversion factor = 1.874799 * e^(-0.003871313*Dw)
> 
> _(Derived from the formulae with D<sub>w</sub> in cm in AAPM Report 204. Note that Report 220 Appendix A clarifies that _D<sub>w</sub>_ should be used, which is reported as 'effective diameter' in Report 204)_

The resulting conversion factors can then be applied to phantom-based dose estimates (Gy*cm or Sv), to achieve a size-specific dose estimate. Of course it makes most sense to do this for every slice of a scan, not just a single slice.

### Sources / suggested reading
AAPM report 220: McCollough C, Bakalyar DM, Bostani M, Brady S, Boedeker K, Boone JM, Chen-Mayer HH, Christianson OI, Leng S, Li B, McNitt-Gray MF. [Use of water equivalent diameter for calculating patient size and size-specific dose estimates (SSDE) in CT: The Report of AAPM Task Group 220](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4991550/). AAPM report. 2014 Sep;2014:6.

AAPM report 204: Boone JM, Strauss KJ, Cody DD, McCollough CH, McNitt‐Gray MF, Toth TL. [Size‐Specific Dose Estimates (SSDE) in Pediatric and Adult Body CT Examinations: Report of AAPM Task Group 204 ...](https://www.aapm.org/pubs/reports/rpt_204.pdf). College Park, MD: American Association of Physicists in Medicine; 2011.

Cheng PM. [Automated estimation of abdominal effective diameter for body size normalization of CT dose](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649058/). Journal of digital imaging. 2013 Jun 1;26(3):406-11.

### Contact

Any questions or comments? Mail me: caspar@verhey.net

If you run into trouble, please mention:
- OS;
- python version;
- whether you have the required libraries installed;
- your command line arguments or python code (screenshots preferred);
- if possible: one of the DICOM files you're trying to use.