# ImageJ Tools


## **Simple autosegmentation (Nuclear segmentation -beta)**


![Raw fluorescence channel](https://github.com/JimageJ/ImageJ-Tools/blob/master/images/fluorescence.gif)
![Segmented label map](https://github.com/JimageJ/ImageJ-Tools/blob/master/images/labelmap.gif)



### **Installation**

Install CLIJ and CLIJ2 by activating their update sites, then copy the **'FRETENATOR_(Rowe et al 2022)'** folder into the Fiji/plugins folder and restart Fiji.

### Implementation

The segmentation tool works by a DoG filter, then Otsu to generate a binary map. I then use a watershed to split objects, but a 3D watershed it a little too severe and causes the loss of many nuclei and many shrink down much smaller than their original size. 

By comparing my watershed to non watersheded binary maps I can create a map of the 'lost nuclei' to add them back in later.

I run a connected components analysis to generate a label map of the watersheded nuclei, and then dilate the labelmap on zero pixels only to fill all the space. I then multiply this by the orginal threshold image to get a a good segmentation with good enough split objects. But this will give incorrect labelling to the 'lost nuclei' present in the image.

To correct this, I run a connected components on the 'lost nuclei' map, to generate  labels, and add on the max value of the OTHER label map. Then I use maximumImage to superimpose these labels on the other label map to get my FINAL label map.

The software will then use the segmentation to quantify statistics (postion, intesnity etc) for each nucleus for the chosen channel.




## **FRETENATOR_Segment_and_ratio (Beta)**

### **Installation**

Install CLIJ and CLIJ2 by activating their update sites, then copy the appropriate folder into the Fiji/plugins folder and restart Fiji. The folders are **'FRETENATOR_(Rowe et al 2022)'** for the version published in the methods chapter Rowe et al (2022) and **'FRETENATOR_with_tracking'**  for the latest version.

### Implementation and usage

Built upon the nuclear segmentation tool, except with the option of a TopHat background removal filter is included. Gives a dialog with segmentation settings, which can be adjusted in real time with a live labelmap max projection preview of frame 1. Pleasse note that the DoG filter and tophat background subtraction are only used to segment the image and are not applied to the channels to be quantified.

The chosen settings will then be applied to the time series and the data for emission ratio calculation etc are output to a results table. This is useful for ratiometric biosensors. Voxels saturated in the **Donor** or **Emission (FRET)** channels are excluded from analysis.

In the latest update, the option of a "nearest point Z projection" is included, which has outline drawing between segmented objects. This will make pretty Z projections where the different objects are discernable and overlayed properly.

![nlsABACUS1-2u ABA treatment quantified and rendered with FRETENATOR](https://github.com/JimageJ/ImageJTools/blob/master/images/Nearest%20point%20emission%20ratios%20of%201-2%20concatenated%20drift%20corrected.gif)


**Usage**:

https://www.youtube.com/watch?v=N91ybNY7Doo


FRETENATOR_Segment_and_ratio produces a Results Table and the following images:

• Threshold map:    ◦ An image of the initial thresholding use for analysis

• Label map:    ◦ An image in which every nucleus is given a value that corresponds to the “label” in the results table.

• Emission ratio map:    ◦ An image in which every nucleus is given the value of it’s emission ratio X 1000

• Max Z projected emission ratio map:    ◦ A maximum Z projection of the emission ratio map

• Nearest point emission ratio map:    ◦ A nearest point projection of the emission ratio map, with outlines added between the nuclei NB: the scale of this image is different to the original image and other images, allowing thin outlines to be drawn.
        

## **FRETENATOR_Labeller (Beta with some alpha functionality)**

### **Installation**
Install CLIJ and CLIJ2 by activating their update sites, then copy the appropriate folder into the Fiji/plugins folder and restart Fiji. The folders are **'FRETENATOR_(Rowe et al 2022)'** for the version published in the methods chapter Rowe et al (2022) and **'FRETENATOR_with_tracking'**  for the latest version.

### Implementation and usage

A follow on tool for after segmentations where users can categorise the ROI in their segmented images. As a work in progress, it currently works on single timepoint 3D label images, allowing users to visually assign labels to one of 10 categories. Results are either output to an existing results table or can be used to measure a chosen image. ***Alpha functionality:*** In the latest version, time course analysis can be performed, but usage asumes the same label usage through time (making it compatable with Trackmate exported files - see below).

**Installation and usage:
**

https://www.youtube.com/watch?v=1rTyM1VBkFc

## **FRETENATOR_Trackmate_Bridge (Alpha)**

A simple plugin to allow **Trackmate 7** analysed label images (Analyse the FRETENATOR label map for tracking then export the tracked label map as dots) to be combined with **FRETENATOR_Segment_and_ratio** output. This adds TrackIDs to the results table and creats a new TrackID labelmap that can be analysed with the ROI manager.



## **Troubleshooting**

All these plugins use CLIJ/CLIJ2 to process images on the graphics card. This means image processing is lightning fast, but also means there are sometimes errors/crashes.

The majority of these crashes are due to one of two reasons:
**i.** the image stack being too large to process on the graphics card this can be solved by using a computer with more video memory, or scaling/cropping the images to be smaller. Normally 4-5x the image size is required in video memory. Running Plugins>ImageJ on GPU (CLIJ2)>Macro tools>CLIJ2 Clinfo will allow you to select GPU and provide info on the hardware’s maximum image size.

or **ii.** out of date graphics card drivers. This often presents with black/blank images. This can often be solved by downloading the latest drivers from the manufacturer website (usually AMD, Nvidia or intel). 
