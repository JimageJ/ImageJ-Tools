"""
******************************************************************************************
		Written by Jim Rowe, Alexander Jones' lab (SLCU, Cambridge).
								Started: 2020-08-06		
							 		@BotanicalJim
							james.rowe at slcu.cam.ac.uk
									Version v1.01

******************************************************************************************
"""


# *******************************import libraries*****************************************
from ij 			import IJ, ImageStack, ImagePlus,CompositeImage
from fiji.util.gui 	import GenericDialogPlus
from ij.process 	import ImageProcessor, StackStatistics, ImageConverter, FloatProcessor
from ij.measure 	import ResultsTable
from array 			import array, zeros
from java.lang 		import Thread
from ij.plugin 		import Slicer

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

def extractFrame(imp, nFrame):
	"""extract a frame from the image, returning a new 16 bit imagePlus labelled with the channel name"""

	stack = imp.getImageStack()
	fr=ImageStack(imp.width, imp.height)
	for i in range(1, imp.getNSlices() + 1):
		for nChannel in range(1, imp.getNChannels()+1):
			index = imp.getStackIndex(nChannel, i, nFrame)
			fr.addSlice(str(i), stack.getProcessor(index))
	imp3 = ImagePlus("Frame " + str(nFrame), fr).duplicate()
	imp3.setDimensions(imp.getNChannels(), imp.getNSlices(), 1)
	comp = CompositeImage(imp3, CompositeImage.COMPOSITE)  
	comp.show()
	return comp


def errorDialog(message):


	gd = NonBlockingGenericDialog("Error")

	gd.addMessage(message)
	gd.showDialog()
	return
	
def concatStacks(masterStack, impToAdd):
	#takes an IMP and adds it to a stack, returning the concatenated stack
	impToAddStack=impToAdd.getImageStack()
	for i in xrange(1, impToAdd.getNSlices()+1):
		try:	
			masterStack.addSlice(impToAddStack.getProcessor(i))	
		except: print "FAILED To addto stack for: "+ impToAdd.getTitle() +" " + str(i)	
	return masterStack

def previewDialog(imp):
	gd = GenericDialogPlus("Nuclear segmentation and quantification v1.01")

	#create a list of the channels in the provided imagePlus
	types = []
	for i in xrange(1, imp.getNChannels()+1):
		types.append(str(i))

	#user can pick which channel to base the segmentation on
	gd.addChoice("Channel number to use for segmentation", types, types[0])
	gd.addChoice("Channel to quantify", types, types[0])
	methods=["Otsu","Default", "Huang", "Intermodes", "IsoData", "IJ_IsoData", "Li", "MaxEntropy", "Mean", "MinError", "Minimum", "Moments", "Percentile", "RenyiEntropy", "Shanbhag", "Triangle", "Yen"]
	gd.addChoice("Autosegmentation method", methods, methods[0])
	intensities=["254", "4094", "65534"]
	gd.addChoice("Max Intensity", intensities, intensities[-1])
	gd.addSlider("Small DoG sigma", 0.5, 10, 1, 0.1)
	gd.addSlider("Large DoG sigma", 0.5, 20, 5 ,0.1)
	gd.addCheckbox("TopHat background subtraction? (Slower, but better) ", True)
	gd.addSlider("TopHat sigma", 5, 20, 8 ,0.1)
	gd.setModal(False)
	gd.addCheckbox("Manually set threshold? ", False)
	gd.addSlider("Manual threshold", 10, 65534, 2000, 1)
	
	gd.hideCancelButton()
	gd.showDialog()

		
	cal = imp.getCalibration()
	pixelAspect=(cal.pixelDepth/cal.pixelWidth)
	
	originalTitle=imp1.getTitle()
	
	choices=gd.getChoices()
	print choices
	sliders=gd.getSliders()
	checkboxes=gd.getCheckboxes()		
	segmentChannel=int(choices.get(0).getSelectedItem())
	quantChannel=int(choices.get(1).getSelectedItem())
	thresholdMethod=choices.get(2).getSelectedItem()
	maxIntensity=int(choices.get(3).getSelectedItem())
	gaussianSigma=sliders.get(0).getValue()/10.0
	largeDoGSigma = gd.sliders.get(1).getValue()/10.0
	topHat=gd.checkboxes.get(0).getState()
	topHatSigma=gd.sliders.get(2).getValue()/10.0

	manualSegment = gd.checkboxes.get(1).getState()
	manualThreshold=gd.sliders.get(3).getValue()
	
	segmentChannelOld=segmentChannel
	thresholdMethodOld=thresholdMethod
	maxIntensityOld=maxIntensity
	gaussianSigmaOld=gaussianSigma
	largeDoGSigmaOld= largeDoGSigma
	topHatOld=topHat
	topHatSigmaOld=topHatSigma
	manualSegmentOld= manualSegment
	manualThresholdOld=manualThreshold
	
	clij2.clear()
	
	segmentImp=extractChannel(imp1, segmentChannel, 0)

	try:
		gfx1=clij2.push(segmentImp)
		gfx2=clij2.create(gfx1)
		gfx3=clij2.create(gfx1)
		gfx4=clij2.create(gfx1)
		gfx5=clij2.create(gfx1)
		gfx7=clij2.create([imp.getWidth(), imp.getHeight()])
	except:	
		try:
		
			Thread.sleep(500)
			IJ.log("Succeeded to sending to graphics card on the second time...")
			gfx1=clij2.push(segmentImp)
			gfx2=clij2.create(gfx1)
			gfx3=clij2.create(gfx1)
			gfx4=clij2.create(gfx1)
			gfx5=clij2.create(gfx1)
			gfx7=clij2.create([imp.getWidth(), imp.getHeight()])
		except:
			errorDialog("""Could not send image to graphics card, it may be too large!
		
			Easy solutions: Try	processing as 8-bit, cropping or scaling the image, or
			select a different CLIJ2 GPU.

			This issue is often intermittent, so trying again may also work! 

			See the "Big Images on x graphics cards' notes at:
			https://clij2.github.io/clij2-docs/troubleshooting for more solutions
			
			"""	+ str(clij2.reportMemory()) )


	gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat, topHatSigma , manualSegment, manualThreshold)
	clij2.maximumZProjection(gfx5, gfx7)

	labelPrevImp= clij2.pull(gfx7)
	IJ.setMinAndMax(labelPrevImp, 0,clij2.getMaximumOfAllPixels(gfx7))
	labelPrevImp.setTitle("Preview segmentation")
	labelPrevImp.show()
	
	IJ.run("glasbey_inverted")
	
	while ((not gd.wasCanceled()) and not (gd.wasOKed())):
		

		segmentChannel=int(choices.get(0).getSelectedItem())
		quantChannel=int(choices.get(1).getSelectedItem())
		thresholdMethod=choices.get(2).getSelectedItem()
		maxIntensity=int(choices.get(3).getSelectedItem())
		gaussianSigma=sliders.get(0).getValue()/10.0
		largeDoGSigma = gd.sliders.get(1).getValue()/10.0
		topHat=gd.checkboxes.get(0).getState()
		topHatSigma=gd.sliders.get(2).getValue()/10.0

		manualSegment = gd.checkboxes.get(1).getState()
		manualThreshold = gd.sliders.get(3).getValue()
		
		if (segmentChannelOld !=segmentChannel or
		thresholdMethodOld !=thresholdMethod or
		maxIntensityOld !=maxIntensity or
		gaussianSigmaOld !=gaussianSigma or
		largeDoGSigmaOld != largeDoGSigma or
		topHatOld !=topHat or
		topHatSigmaOld !=topHatSigma or
		manualSegmentOld != manualSegment or
		manualThresholdOld !=manualThreshold
		):

			if segmentChannelOld!=segmentChannel:
					clij2.clear()
					segmentImp=extractChannel(imp1, segmentChannel, 0)
					gfx1=clij2.push(segmentImp)
					gfx2=clij2.create(gfx1)
					gfx3=clij2.create(gfx1)
					gfx4=clij2.create(gfx1)
					gfx5=clij2.create(gfx1)
					gfx7=clij2.create([imp.getWidth(), imp.getHeight()])
			gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat,topHatSigma, manualSegment, manualThreshold)
			clij2.maximumZProjection(gfx5, gfx7)
			labelPrevImp.close()
			labelPrevImp= clij2.pull(gfx7)
			IJ.setMinAndMax(labelPrevImp, 0,clij2.getMaximumOfAllPixels(gfx7))
			labelPrevImp.setTitle("Preview segmentation")
			labelPrevImp.show()
			
			IJ.run("glasbey_inverted")
		
		segmentChannelOld=segmentChannel
		thresholdMethodOld=thresholdMethod
		maxIntensityOld=maxIntensity
		gaussianSigmaOld=gaussianSigma
		largeDoGSigmaOld= largeDoGSigma
		topHatOld=topHat
		topHatSigmaOld=topHatSigma

		manualSegmentOld= manualSegment
		manualThresholdOld=manualThreshold
		
		Thread.sleep(200)
	labelPrevImp.close()
	
	return segmentChannel, quantChannel, thresholdMethod, maxIntensity, gaussianSigma, largeDoGSigma, topHat, topHatSigma, manualSegment, manualThreshold
	
	
def segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat, topHatSigma, manualSegment, manualThreshold):
	


	# DoG filter for background normalised segmentation. NB. Kernel is Z-normalised to pixel aspect ratio
	if topHat == True :
		clij2.topHatBox(gfx1, gfx3, topHatSigma, topHatSigma, 2)
		clij2.differenceOfGaussian3D(gfx3, gfx2, gaussianSigma, gaussianSigma, 1+(gaussianSigma-1)/pixelAspect, largeDoGSigma, largeDoGSigma,largeDoGSigma/pixelAspect)

	else:
		clij2.differenceOfGaussian3D(gfx1, gfx2, gaussianSigma, gaussianSigma, 1+(gaussianSigma-1)/pixelAspect, largeDoGSigma, largeDoGSigma,largeDoGSigma/pixelAspect)

	if manualSegment == True :
		clij2.threshold(gfx2, gfx3, manualThreshold)

	else:
		#auto threshold and watershed to seed the object splitting
		clij2.automaticThreshold(gfx2, gfx3, thresholdMethod)
	

	clij2.watershed(gfx3,gfx2)
	

	
	# add watershed to original threshold, and then use this to generate a binary image of any ROI lost in watershed process
	clij2.addImages(gfx2, gfx3, gfx5)
	clij2.floodFillDiamond(gfx5, gfx4, 1, 2)
	clij2.replaceIntensity(gfx4, gfx5, 2, 0)
	
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
	clij2.connectedComponentsLabelingDiamond(gfx5, gfx4)
	clij2.addImageAndScalar(gfx4, gfx5, (1 + watershedLabelMax))
	#delete the background and combine the two images
	clij2.replaceIntensity(gfx5, gfx4,(1 + watershedLabelMax), 0)
	clij2.maximumImages(gfx4, gfx2, gfx5)
	
	
	#gfx3 = threshold channel, gfx5 = label image, gfx1=original image, gfx2 & gfx4 & gfx5 are junk
	
	return gfx1,gfx2,gfx3,gfx4,gfx5


	
def quantify(quantgfx,labelgfx, table, nFrame, originalTitle):
	results=ResultsTable()
	clij2.statisticsOfBackgroundAndLabelledPixels(gfx4, gfx5, results)

	for i in range(results.size()):
		table.incrementCounter()
		table.addValue("Frame (Time)", nFrame)
		table.addValue("Label", i)
		table.addValue("MEAN_INTENSITY",results.getValue("MEAN_INTENSITY",i))
		table.addValue("SUM_INTENSITY",results.getValue("SUM_INTENSITY",i))
		table.addValue("MINIMUM_INTENSITY",results.getValue("MINIMUM_INTENSITY",i))
		table.addValue("MAXIMUM_INTENSITY",results.getValue("MAXIMUM_INTENSITY",i))
		table.addValue("STANDARD_DEVIATION_INTENSITY",results.getValue("STANDARD_DEVIATION_INTENSITY",i))
		table.addValue("PIXEL_COUNT",results.getValue("PIXEL_COUNT",i))
		table.addValue("CENTROID_X",results.getValue("CENTROID_X",i))
		table.addValue("CENTROID_Y",results.getValue("CENTROID_Y",i))
		table.addValue("CENTROID_Z",results.getValue("CENTROID_Z",i))
		
		table.addValue("File name", originalTitle)
		
	return table

# *****************************body of code starts****************************************


#give install instructions for CLIJ if not installed

try: 
	from net.haesleinhuepf.clij2 import CLIJ2

except:
	errorDialog("""This plugin requires clij2 to function. 
	
	To install please follow these instructions: 
	
	1. Click Help>Update> Manage update sites
	2. Make sure the "clij2" update site is selected.
	3. Click Close> Apply changes.
	4. Close and reopen ImageJ""")


clij2 = CLIJ2.getInstance()
clij2.clear()


#get the current image
imp1= IJ.getImage()

#define inputs (to be put in a dialog if I automate) 


options= previewDialog(imp1)
print(options)
segmentChannel, quantChannel, thresholdMethod, maxIntensity, gaussianSigma, largeDoGSigma, topHat, topHatSigma, manualSegment, manualThreshold =options
totalFrames=imp1.getNFrames() +1

#table is the final results table
table = ResultsTable()

clij2 = CLIJ2.getInstance()
clij2.clear()

#get the pixel aspect for use in zscaling kernels for filters
cal = imp1.getCalibration()
pixelAspect=(cal.pixelDepth/cal.pixelWidth)
originalTitle=imp1.getTitle()

conThresholdStack=ImageStack(imp1.width, imp1.height)
conlabelImpStack=ImageStack(imp1.width, imp1.height)

	
for nFrame in xrange(1, totalFrames):
	clij2.clear()
	segmentImp=extractChannel(imp1, segmentChannel, nFrame)
	quantImp=extractChannel(imp1, quantChannel, nFrame)
	gfx1=clij2.push(segmentImp)
	gfx2=clij2.create(gfx1)
	gfx3=clij2.create(gfx1)
	gfx4=clij2.create(gfx1)
	gfx5=clij2.create(gfx1)
	gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat,topHatSigma, manualSegment, manualThreshold)
	
	thresholdImp = clij2.pull(gfx3)
	labelImp = clij2.pull(gfx5)
	gfx4=clij2.push(quantImp)
	IJ.setMinAndMax(thresholdImp, 0,1)
	thresholdImp.setCalibration(cal)
	thresholdImp.setTitle("Binary mask of "+originalTitle)
	
	

	#add the images to concatenated stacks
	conThresholdStack = concatStacks(conThresholdStack, thresholdImp)
	conlabelImpStack=concatStacks(conlabelImpStack, labelImp)
	table=quantify(gfx4, gfx5, table, nFrame, originalTitle)
	
	thresholdImp.close()
	labelImp.close()
	IJ.log( "Processing timeframe: " +str(nFrame))
table.show("Results of "+originalTitle)
#Show the images and make the images pretty... I should have put in a function`

conThresholdImp= ImagePlus( "Threshold image for "+ originalTitle, conThresholdStack)
conThresholdImp.setDimensions(1,  imp1.getNSlices(), imp1.getNFrames())
IJ.setMinAndMax(conThresholdImp, 0,1)
conThresholdImp.setCalibration(cal)
conThresholdImp = CompositeImage(conThresholdImp, CompositeImage.COMPOSITE)
conThresholdImp.show()

	
conlabelImp= ImagePlus("Label map "+ originalTitle, conlabelImpStack)
conlabelImp.setDimensions(1, imp1.getNSlices(), imp1.getNFrames())
conlabelImp.setCalibration(cal)
stats=StackStatistics(conlabelImp)
conlabelImp = CompositeImage(conlabelImp, CompositeImage.COMPOSITE)  
IJ.setMinAndMax(conlabelImp, 0,stats.max)
conlabelImp.show()
IJ.run("glasbey_inverted")

