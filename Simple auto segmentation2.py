"""
******************************************************************************************
						Autosegmentation for nuclei. V0.2
			
			Written by Jim Rowe, Alexander Jones' lab (SLCU, Cambridge).
									2020-07-07		
							 		@BotanicalJim
							james.rowe at slcu.cam.ac.uk

******************************************************************************************
"""



# *******************************import libraries*****************************************
from ij import IJ, ImageStack, ImagePlus
from fiji.util.gui import GenericDialogPlus
from ij.process import ImageProcessor, StackStatistics, ImageConverter, FloatProcessor
from ij.measure import ResultsTable
from array import array, zeros


# *******************************functions************************************************


def extractChannel(imp, nChannel, nFrame):
	"""extract a channel from the image, at a given frame returning a new imagePlus labelled with the channel name"""

	stack = imp.getImageStack()
	ch=ImageStack(imp.width, imp.height)
	for i in range(imp.getNSlices()):
		index = imp.getStackIndex(nChannel, i, nFrame)
		ch.addSlice(str(i), stack.getProcessor(index))
	imp3 = ImagePlus("Channel " + str(nChannel), ch).duplicate()
	stats =StackStatistics(imp3) 
	IJ.setMinAndMax(imp3, stats.min, stats.max)
	return imp3


def errorDialog(message):


	gd = NonBlockingGenericDialog("Error")

	gd.addMessage(message)
	gd.showDialog()
	return



# *****************************body of code starts*********************************


#give install instructions for CLIJ if not installed

try: 
	from net.haesleinhuepf.clij2 import CLIJ2

except:
	errorDialog("""This plugin requires clij to function. 
	
	To install please follow these instructions: 
	
	1. Click Help>Update> Manage update sites
	2. Make sure the "clij2" and "clij" update sites are selected.
	3. Click Close> Apply changes.
	4. Close and reopen ImageJ""")


clij2 = CLIJ2.getInstance()
clij2.clear()


#get the current image
imp1= IJ.getImage()

#define inputs (to be put in a dialog if I automate) 
nFrame=0
donorChannel=1
acceptorChannel=2
segmentChannel=3
gaussianSigma=1.2
thresholdMethod="Otsu"
maxIntensity=4094
DoGRatio = 9

#get the pixel aspect for use in zscaling kernels for filters
cal=imp1.getCalibration()
pixelAspect=(cal.pixelDepth/cal.pixelWidth)
donorImp=extractChannel(imp1, donorChannel, nFrame)
acceptorImp=extractChannel(imp1, acceptorChannel, nFrame)
segmentImp=extractChannel(imp1, segmentChannel, nFrame)
originalTitle=imp1.getTitle()


gfx1=clij2.push(segmentImp)

gfx2=clij2.create(gfx1)
gfx3=clij2.create(gfx1)
gfx4=clij2.create(gfx1)

# DoG filter for background normalised segmentation. NB. Kernel is Z-normalised to pixel aspect ratio

clij2.differenceOfGaussian3D(gfx1, gfx2, gaussianSigma, gaussianSigma, 1+(gaussianSigma-1)/pixelAspect, gaussianSigma*DoGRatio, gaussianSigma*DoGRatio, gaussianSigma*DoGRatio/pixelAspect)

#auto threshold and watershed to seed the object splitting
clij2.automaticThreshold(gfx2, gfx3, thresholdMethod)
clij2.watershed(gfx3,gfx2)

# add watershed to original image, and then use this to generate a binary image of any ROI lost in watershed process
clij2.addImages(gfx2, gfx3, gfx1)
clij2.floodFillDiamond(gfx1, gfx4, 1, 2)
clij2.replaceIntensity(gfx4, gfx1, 2, 0)

#label watershed image
clij2.connectedComponentsLabelingDiamond(gfx2, gfx4)

#dilate all the labeled watershed ROI out (only onto zero labeled pixels), then multiply this by original binary map, to get labeled ROI
for i in range(30):
	#I'm not sure why it needs the second argument image (gfx3) here... It doesn't seem to affect the results...
	clij2.onlyzeroOverwriteMaximumBox(gfx4, gfx3, gfx2) 
	clij2.onlyzeroOverwriteMaximumDiamond(gfx2, gfx3, gfx4)
clij2.multiplyImages(gfx4,gfx3, gfx2)

#label the missed ROI then add on the largest value from the other labelled image (so they can be combined)
watershedLabelMax =clij2.getMaximumOfAllPixels(gfx2)
clij2.connectedComponentsLabelingDiamond(gfx1, gfx4)
clij2.addImageAndScalar(gfx4, gfx1, (1 + watershedLabelMax))

#delete the background and combine the two images
clij2.replaceIntensity(gfx1, gfx4,(1 + watershedLabelMax), 0)
clij2.maximumImages(gfx4, gfx2, gfx1)


#gfx1 = label image,  gfx3 is binary map, gfx2 & gfx4 are junk

#get the stats from the original image channel
results=ResultsTable()
clij2.release(gfx2)
gfx2=clij2.push(segmentImp)
clij2.statisticsOfBackgroundAndLabelledPixels(gfx2, gfx1, results)
results.show(originalTitle +" segmentation results (pixel scaled, not calibrated)")

#show images

thresholdImp = clij2.pull(gfx3)
thresholdImp.show()
IJ.setMinAndMax(thresholdImp, 0,1)
thresholdImp.setCalibration(cal)
thresholdImp.setTitle("Binary mask of "+originalTitle)

labelImp = clij2.pull(gfx1)
labelImp.show()
labelImp.setCalibration(cal)
IJ.setMinAndMax(labelImp, 0, clij2.getMaximumOfAllPixels(gfx1))
IJ.run("glasbey_inverted")
labelImp.setTitle("Label map of "+originalTitle)



#Cleanup!
clij2.clear()
