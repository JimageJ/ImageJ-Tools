# ImageJTools


Nuclear segmentation

The segmentation tool works by a DoG filter, then Otsu to generate a binary map. I then use a watershed to split objects, but a 3D watershed it a little too severe and causes the loss of many nuclei and many shrink down much smaller than their original size. 

By comparing my watershed to non watersheded binary maps I can create a map of the 'lost nuclei' to add them back in later.

I run a connected components analysis to generate a label map of the watersheded nuclei, and then dilate the labelmap on zero pixels only to fill all the space. I then multiply this by the orginal threshold image to get a a good segmentation with good enough split objects. But this will give incorrect labelling to the 'lost nuclei' present in the image.

To correct this, I run a connected components on the 'lost nuclei' map, to generate  labels, and add on the max value of the OTHER label map. Then I use maximumImage to superimpose these labels on the other label map to get my FINAL label map.




Timeseries segmentation and ratiometric analysis

Built upon the nuclear segmentation tool. Gives a dialog with segmentation settings, which can be adjusted in real time with a live labelmap preview of frame 1.THe chosen settings will then be applied to the time series and the data for emission ratio calculation etc are output to a resultstable. Voxels saturated in the donor or emission (FRET) channels are excluded from analysis.
