# ImageJ Tools


**Simple autosegmentation (Nuclear segmentation -beta)**

The segmentation tool works by a DoG filter, then Otsu to generate a binary map. I then use a watershed to split objects, but a 3D watershed it a little too severe and causes the loss of many nuclei and many shrink down much smaller than their original size. 

By comparing my watershed to non watersheded binary maps I can create a map of the 'lost nuclei' to add them back in later.

I run a connected components analysis to generate a label map of the watersheded nuclei, and then dilate the labelmap on zero pixels only to fill all the space. I then multiply this by the orginal threshold image to get a a good segmentation with good enough split objects. But this will give incorrect labelling to the 'lost nuclei' present in the image.

To correct this, I run a connected components on the 'lost nuclei' map, to generate  labels, and add on the max value of the OTHER label map. Then I use maximumImage to superimpose these labels on the other label map to get my FINAL label map.

The software will then use the segmentation to quantify statistics (postion, intesnity etc) for each nucleus for the chosen channel.




**FRETENATOR_Segment_and_ratio (Beta)**

Built upon the nuclear segmentation tool, except with the option of a TopHat background removal filter is included. Gives a dialog with segmentation settings, which can be adjusted in real time with a live labelmap max projection preview of frame 1. Pleasse note that the DoG filter and tophat background subtraction are only used to segment the image and are not applied to the channels to be quantified.

The chosen settings will then be applied to the time series and the data for emission ratio calculation etc are output to a results table. This is useful for ratiometric biosensors. Voxels saturated in the **Donor** or **Emission (FRET)** channels are excluded from analysis.

In the latest update, the option of a "nearest point Z projection" is included, which has outline drawing between segmented objects. This will make pretty Z projections where the different objects are discernable and overlayed properly.

![nlsABACUS1-2u ABA treatment quantified and rendered with FRETENATOR](https://github.com/JimageJ/ImageJTools/blob/master/Nearest%20point%20emission%20ratios%20of%201-2%20concatenated%20drift%20corrected.gif)


Installation:

https://www.youtube.com/watch?v=_mALvThK24Y

Usage:

https://www.youtube.com/watch?v=N91ybNY7Doo


FRETENATOR_Segment_and_ratio produces a Results Table and the following images:

• Threshold map:    ◦ An image of the initial thresholding use for analysis

• Label map:    ◦ An image in which every nucleus is given a value that corresponds to the “label” in the results table.

• Emission ratio map:    ◦ An image in which every nucleus is given the value of it’s emission ratio X 1000

• Max Z projected emission ratio map:    ◦ A maximum Z projection of the emission ratio map

• Nearest point emission ratio map:    ◦ A nearest point projection of the emission ratio map, with outlines added between the nuclei NB: the scale of this image is different to the original image and other images, allowing thin outlines to be drawn.
        

**FRETENATOR_Labeller (Alpha)**

A follow on tool for after segmentations where users can categorise the ROI in their segmented images. As a work in progress, it currently works on single timepoint 3D label images, allowing users to visually assign labels to one of 10 categories. Results are either output to an existing results table or can be used to measure a chosen image. It will work with labelmaps up to 4095 labels currently.

Installation and usage:

https://www.youtube.com/watch?v=1rTyM1VBkFc

