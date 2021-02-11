# ImageJTools


**Nuclear segmentation**

The segmentation tool works by a DoG filter, then Otsu to generate a binary map. I then use a watershed to split objects, but a 3D watershed it a little too severe and causes the loss of many nuclei and many shrink down much smaller than their original size. 

By comparing my watershed to non watersheded binary maps I can create a map of the 'lost nuclei' to add them back in later.

I run a connected components analysis to generate a label map of the watersheded nuclei, and then dilate the labelmap on zero pixels only to fill all the space. I then multiply this by the orginal threshold image to get a a good segmentation with good enough split objects. But this will give incorrect labelling to the 'lost nuclei' present in the image.

To correct this, I run a connected components on the 'lost nuclei' map, to generate  labels, and add on the max value of the OTHER label map. Then I use maximumImage to superimpose these labels on the other label map to get my FINAL label map.




**FRETENATOR_Segment_and_ratio**

Built upon the nuclear segmentation tool, except with the option of a TopHat background removal filter is included. Gives a dialog with segmentation settings, which can be adjusted in real time with a live labelmap max projection preview of frame 1.The chosen settings will then be applied to the time series and the data for emission ratio calculation etc are output to a results table. This is useful for ratiometric biosensors. Voxels saturated in the **Donor** or **Emission (FRET)** channels are excluded from analysis.

In the latest update, the option of a "nearest point Z projection" is included, which has outline drawing between segmented objects. This will make pretty Z projections where the different objects are discernable and overlayed properly.

![nlsABACUS1-2u ABA treatment quantified and rendered with FRETENATOR](https://github.com/JimageJ/ImageJTools/blob/master/Nearest%20point%20emission%20ratios%20of%201-2%20concatenated%20drift%20corrected.gif)


Installation:

https://www.youtube.com/watch?v=_mALvThK24Y

Usage:

https://www.youtube.com/watch?v=N91ybNY7Doo

**FRETENATOR_labeller**

A follow on tool for after segmentations where users can categorise the ROI in their segmented images. As a work in progress it currently works on single timepoint 2 or 3D label image, allowing users to visually assign labels to one of 10 categories, but doesn't output the results table yet. It will work with any labelmaps up to 4095 labels currently.

