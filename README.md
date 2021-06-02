# DICOMwaterequivalent
This is a python 3 script / program to calculate the patient's water equivalent area (_A<sub>w</sub>_), water equivalent circle diameter (_D<sub>w</sub>_), and area-equivalent diameter, from 16 bit CT DICOM images.

_A<sub>w</sub>_ and _D<sub>w</sub>_ consider tissue attenuation as proposed by AAPM Task Groups 204 and 220 for calculating the patient size for size-specific dose estimates (SSDE) in CT. The area-equivalent diameter only describes the patient geometry and could be used as another measurement of patient size, for instance to impute missing BMI data when patient length is available.

This script can be used as a [Python function](#python-function) or as a [standalone Python script](#standalone).

> :warning: Always check the output image for correct ROI placement. The ROI is automatically placed around the largest contour with HUs above the ROI HU threshold. You must manually set the ROI HU threshold. Confirm that the patient contour is inside the displayed ROI outline, and that the ROI does not include the CT examination table, air, clothing, implants, ECG leads etc. Exclusion of implants is not (yet) possible with this script.

> :warning: This software and its results should not be used blindly without adequate professional judgment. Read LICENSE for further disclaimers.

## Contents
* [Requirements](#requirements)
* [Python function](#python-function)
  + [Usage](#usage)
  + [Returns](#returns)
  + [Example](#example)
* [Standalone](#standalone)
  + [Usage](#usage-1)
  + [Output](#output)
  + [Example](#example-1)
* [More information](#more-information)
  + [Using SSDE factors](#using-ssde-factors)
  + [Sources / suggested reading](#sources---suggested-reading)
  + [Contact](#contact)

## Requirements
Modules `cv2` and `pydicom`:

    $ pip3 install opencv-python pydicom

Download the file `DICOMwaterequivalent.py` and place it in your working directory. Alternatively, you can put it in one of the other directories Python checks for modules. To list these directories:

    $ python3 -c 'import sys; print(sys.path)'

## Python function
You can call DICOMwaterequivalent() from your own python script.

### Usage

```python
>>> import DICOMwaterequivalent
>>> DICOMwaterequivalent(filename, threshold, window)
```

* filename:  DICOM file (absolute or relative path).
* threshold: ROI contour threshold level (in HU).
* window:    (optional) view window for output image, as tuple (ww,wl). If omitted, no image will be outputted.

### Returns
Tuple containing:
- [0]  water equivalent area _A<sub>w</sub>_ in mm² (float),
- [1]  water equivalent diameter _D<sub>w</sub>_ in mm (float),
- [2]  ROI area in mm² (float),
- [3]  ROI area-equivalent circle diameter in mm (float),
- [4]  ROI hull area in mm² (float),
- [5]  ROI hull area-equivalent circle diameter in mm(float),
- [6]  image displaying ROI and ROI hull contours (numpy array).

### Example

```python
>>> import DICOMwaterequivalent
>>> equiv = DICOMwaterequivalent('480.0.dcm', -250, (1000,40))
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
```

## Standalone
You can call DICOMwaterequivalent.py from the command line.

### Usage

    $ ./DICOMwaterequivalent.py <filename> <threshold> <ww> <wl>

* filename:  DICOM file (absolute or relative path).
* threshold: ROI contour threshold level in HU.
* ww: window width (optional, default: 1600).
* wl: window level (optional, default: -400).

You need to specify both ww and wl, or neither.

### Output
##### Console
```
(
	water equivalent area Aw in mm² (float),
	water equivalent circle diameter Dw in mm (float),
	ROI area in mm² (float),
	ROI area-equivalent circle diameter in mm (float),
	ROI hull area in mm² (float),
	ROI hull area-equivalent circle diameter in mm (float)
)
```

##### Graphic
image displaying ROI and ROI hull contours (press any key to close & continue)

### Example

    $ ./DICOMwaterequivalent.py 480.0.dcm -250
    (24740.231323242188, 177.48307205659782, 27518.49097592727, 187.18341518945613, 25731.055450439453, 181.0022025481258)
<img align="left" src="screenshot.png" />
<br clear="all" />
* Example source image courtesy of Patient Contributed Image Repository patient 54879843, available from http://www.pcir.org/researchers/downloads_available.html

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

The resulting conversion factors can then be applied to phantom-based dose estimates (Gy*cm or Sv), to achieve a size-specific dose estimate.

### Sources / suggested reading
AAPM report 220: McCollough C, Bakalyar DM, Bostani M, Brady S, Boedeker K, Boone JM, Chen-Mayer HH, Christianson OI, Leng S, Li B, McNitt-Gray MF. [Use of water equivalent diameter for calculating patient size and size-specific dose estimates (SSDE) in CT: The Report of AAPM Task Group 220](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4991550/). AAPM report. 2014 Sep;2014:6.

AAPM report 204: Boone JM, Strauss KJ, Cody DD, McCollough CH, McNitt‐Gray MF, Toth TL. [Size‐Specific Dose Estimates (SSDE) in Pediatric and Adult Body CT Examinations: Report of AAPM Task Group 204 ...](https://www.aapm.org/pubs/reports/rpt_204.pdf). College Park, MD: American Association of Physicists in Medicine; 2011.

Cheng PM. [Automated estimation of abdominal effective diameter for body size normalization of CT dose](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649058/). Journal of digital imaging. 2013 Jun 1;26(3):406-11.

### Contact

Any questions or comments? Mail me: caspar@verhey.net