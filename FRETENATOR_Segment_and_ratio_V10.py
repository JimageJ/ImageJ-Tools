"""
******************************************************************************************
		Written by Jim Rowe, Alexander Jones' lab (SLCU, Cambridge).
								Started: 2020-08-06		
							 		@BotanicalJim
							james.rowe at slcu.cam.ac.uk
									Version 1.10.1



******************************************************************************************
"""


# *******************************import libraries*****************************************
from ij import IJ, ImageStack, ImagePlus,CompositeImage
from fiji.util.gui import GenericDialogPlus
from ij.process import ImageProcessor, StackStatistics, ImageConverter, FloatProcessor
from ij.measure import ResultsTable
from array import array, zeros
from java.lang import Thread
from ij.plugin import Slicer

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
	gd = GenericDialogPlus("FRETENATOR")

	#create a list of the channels in the provided imagePlus
	types = []
	for i in xrange(1, imp.getNChannels()+1):
		types.append(str(i))
	gd.addMessage("""Rowe, J. H, Rizza, A., Jones A. M. (2021) Quantifying phytohormones
	in vivo with FRET biosensors and the FRETENATOR analysis toolset
	Methods in Molecular Biology""")
	#user can pick which channel to base the segmentation on
	try:
		gd.addChoice("Channel number to use for segmentation", types, types[2])
	except: gd.addChoice("Channel number to use for segmentation", types, types[1])
	gd.addChoice("Channel number to use for donor", types, types[0])
	gd.addChoice("Channel number to use for acceptor (FRET)", types, types[1])
	try:
		gd.addChoice("Channel number to use for acceptor", types, types[2])
	except: gd.addChoice("Channel number to use for acceptor", types, types[1])
	
	methods=["Otsu","Default", "Huang", "Intermodes", "IsoData", "IJ_IsoData", "Li", "MaxEntropy", "Mean", "MinError", "Minimum", "Moments", "Percentile", "RenyiEntropy", "Shanbhag", "Triangle", "Yen"]
	gd.addChoice("Autosegmentation method", methods, methods[0])
	intensities=["254", "4094", "65534"]
	gd.addChoice("Max Intensity", intensities, intensities[-1])
	gd.addSlider("Small DoG sigma", 0.5, 10, 1.2, 0.1)
	gd.addSlider("Large DoG sigma", 0.5, 20, 6 ,0.1)
	gd.addCheckbox("TopHat background subtraction? (Slower, but better) ", True)
	gd.addSlider("TopHat sigma", 5, 20, 8 ,0.1)
	gd.setModal(False)
	gd.addCheckbox("Manually set threshold? ", False)
	gd.addSlider("Manual threshold", 10, 65534, 2000, 1)
	dilationOptions=["0", "1", "2","3", "4", "5", "6"]
	gd.addChoice("Dilation?", dilationOptions, "0")
	gd.addCheckbox("Size exclusion of ROI? ", False)
	gd.addSlider("Minimum ROI size", 0, 9999, 0, 1)
	gd.addSlider("Maximum ROI size", 1, 10000, 10000, 1)
	gd.addCheckbox("Create nearest point projection with outlines (SLOW)? ", False)
	gd.showDialog()

		
	cal = imp.getCalibration()
	pixelAspect=(cal.pixelDepth/cal.pixelWidth)
	
	originalTitle=imp1.getTitle()
	
	choices=gd.getChoices()
	sliders=gd.getSliders()
	checkboxes=gd.getCheckboxes()		
	segmentChannel=int(choices.get(0).getSelectedItem())
	donorChannel=int(choices.get(1).getSelectedItem())
	acceptorChannel=int(choices.get(2).getSelectedItem())
	acceptorChannel2=int(choices.get(3).getSelectedItem())
	thresholdMethod=choices.get(4).getSelectedItem()
	maxIntensity=int(choices.get(5).getSelectedItem())
	gaussianSigma=sliders.get(0).getValue()/10.0
	largeDoGSigma = gd.sliders.get(1).getValue()/10.0
	topHat=gd.checkboxes.get(0).getState()
	topHatSigma=gd.sliders.get(2).getValue()/10.0
	
	manualSegment = gd.checkboxes.get(1).getState()
	manualThreshold=gd.sliders.get(3).getValue()
	dilation=int(choices.get(6).getSelectedItem())
	sizeExclude=gd.checkboxes.get(2).getState()
	minSize = gd.sliders.get(4).getValue()
	maxSize = gd.sliders.get(5).getValue()
	#print dir(gd.sliders.get(5))
	#print maxSize
	
	segmentChannelOld=segmentChannel
	thresholdMethodOld=thresholdMethod
	maxIntensityOld=maxIntensity
	gaussianSigmaOld=gaussianSigma
	largeDoGSigmaOld= largeDoGSigma
	topHatOld=topHat
	topHatSigmaOld=topHatSigma
	manualSegmentOld= manualSegment
	manualThresholdOld=manualThreshold
	dilationOld=dilation
	sizeExcludeOld=sizeExclude
	minSizeOld=minSize
	maxSizeOld=maxSize
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
			print("Succeeded to sending to graphics card on the second time...")
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


	gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat, topHatSigma , manualSegment, manualThreshold, dilation,sizeExclude, minSize, maxSize)
	clij2.maximumZProjection(gfx5, gfx7)

	labelPrevImp= clij2.pull(gfx7)
	IJ.setMinAndMax(labelPrevImp, 0,clij2.getMaximumOfAllPixels(gfx7))
	labelPrevImp.setTitle("Preview segmentation")
	labelPrevImp.show()
	
	IJ.run("glasbey_inverted")
	
	while ((not gd.wasCanceled()) and not (gd.wasOKed())):
		

		segmentChannel=int(choices.get(0).getSelectedItem())
		donorChannel=int(choices.get(1).getSelectedItem())
		acceptorChannel=int(choices.get(2).getSelectedItem())
		acceptorChannel2=int(choices.get(3).getSelectedItem())
		thresholdMethod=choices.get(4).getSelectedItem()
		maxIntensity=int(choices.get(5).getSelectedItem())
		gaussianSigma=sliders.get(0).getValue()/10.0
		largeDoGSigma = gd.sliders.get(1).getValue()/10.0
		topHat=gd.checkboxes.get(0).getState()
		topHatSigma=gd.sliders.get(2).getValue()/10.0

		manualSegment = gd.checkboxes.get(1).getState()
		manualThreshold = gd.sliders.get(3).getValue()
		
		dilation=int(choices.get(6).getSelectedItem())
		
		sizeExclude=gd.checkboxes.get(2).getState()
		minSize = gd.sliders.get(4).getValue()
		maxSize = gd.sliders.get(5).getValue()
		
			
	
		if (segmentChannelOld !=segmentChannel or
		thresholdMethodOld !=thresholdMethod or
		maxIntensityOld !=maxIntensity or
		gaussianSigmaOld !=gaussianSigma or
		largeDoGSigmaOld != largeDoGSigma or
		topHatOld !=topHat or
		topHatSigmaOld !=topHatSigma or
		manualSegmentOld != manualSegment or
		manualThresholdOld !=manualThreshold or
		dilation != dilationOld or
		sizeExcludeOld!=sizeExclude or
		minSizeOld!=minSize or
		maxSizeOld!=maxSize
		):
			if minSizeOld!=minSize:
				if minSize>=maxSize:
					maxSize=minSize+1
					gd.sliders.get(5).setValue(maxSize)
			if maxSizeOld!=maxSize:
				if minSize>=maxSize:
					minSize=maxSize-1
					gd.sliders.get(4).setValue(minSize)
			if segmentChannelOld!=segmentChannel:
					clij2.clear()
					segmentImp=extractChannel(imp1, segmentChannel, 0)
					gfx1=clij2.push(segmentImp)
					gfx2=clij2.create(gfx1)
					gfx3=clij2.create(gfx1)
					gfx4=clij2.create(gfx1)
					gfx5=clij2.create(gfx1)
					gfx7=clij2.create([imp.getWidth(), imp.getHeight()])
			gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat,topHatSigma, manualSegment, manualThreshold, dilation,sizeExclude, minSize, maxSize)
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
		largeDoGSigmaOld = largeDoGSigma
		topHatOld=topHat
		topHatSigmaOld=topHatSigma
		manualSegmentOld= manualSegment
		manualThresholdOld=manualThreshold
		dilationOld=dilation
		sizeExcludeOld=sizeExclude
		minSizeOld=minSize
		maxSizeOld=maxSize
		Thread.sleep(200)
	labelPrevImp.close()
	makeNearProj = gd.checkboxes.get(3).getState()
	return segmentChannel, donorChannel, acceptorChannel, acceptorChannel2, thresholdMethod, maxIntensity, gaussianSigma, largeDoGSigma, topHat, topHatSigma, manualSegment, manualThreshold, makeNearProj, dilation, sizeExclude, minSize, maxSize
	
	
def segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat, topHatSigma, manualSegment, manualThreshold, dilation, sizeExclude, minSize, maxSize):
	


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
	for i in range(25):
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

	if sizeExclude:
		clij2.excludeLabelsOutsideSizeRange(gfx5, gfx4, minSize, maxSize)
		clij2.copy(gfx4, gfx5)

	if dilation:
		for i in range(dilation):
			if (i % 2) == 0:
				clij2.onlyzeroOverwriteMaximumDiamond(gfx5, gfx3, gfx4) 
			else:
				clij2.onlyzeroOverwriteMaximumBox(gfx5, gfx3, gfx4) 
			clij2.copy(gfx4, gfx5)

	if dilation:
		for i in range(dilation):
			if (i % 2) == 0:
				clij2.onlyzeroOverwriteMaximumDiamond(gfx3, gfx5, gfx4) 
			else:
				clij2.onlyzeroOverwriteMaximumBox(gfx3, gfx5, gfx4) 
			clij2.copy(gfx4, gfx3)
	#gfx3 = threshold channel, gfx5 = label image, gfx1=original image, gfx2 & gfx4 & gfx5 are junk
	
	return gfx1,gfx2,gfx3,gfx4,gfx5

def fretCalculations(imp1, nFrame, donorChannel, acceptorChannel, acceptorChannel2, table, gfx1, gfx2, gfx3, gfx4, gfx5, originalTitle):
	donorImp=extractChannel(imp1, donorChannel, nFrame)
	acceptorImp=extractChannel(imp1, acceptorChannel, nFrame)
	acceptorImp2=extractChannel(imp1, acceptorChannel2, nFrame)
	
	#push donor and acceptor channels to gpu and threshold them both to remove saturated pixels
	
	gfx4=clij2.push(donorImp)
	gfx5=clij2.push(acceptorImp)
	gfx6=clij2.create(gfx5)
	
	clij2.threshold(gfx4,gfx2, maxIntensity)
	clij2.binarySubtract(gfx3, gfx2, gfx6)
	
	clij2.threshold(gfx5,gfx2, maxIntensity)
	clij2.binarySubtract(gfx6, gfx2, gfx3)
	
	clij2.threshold(gfx3,gfx6, 0.5)
	clij2.multiplyImages(gfx6, gfx4, gfx2)
	clij2.multiplyImages(gfx6, gfx5, gfx4)
	
	
	
	
	gfx6=clij2.push(acceptorImp2)
	
	#donor is gfx2, acceptor FRET is gfx4, segment channel (acceptor normal) is gfx6
	
	results=ResultsTable()
	clij2.statisticsOfBackgroundAndLabelledPixels(gfx2, gfx1, results)
	
	donorChIntensity=results.getColumn(13)
	results2=ResultsTable()
	clij2.statisticsOfBackgroundAndLabelledPixels(gfx4, gfx1, results2)
	acceptorChIntensity=results2.getColumn(13)
	
	results3=ResultsTable()
	clij2.statisticsOfBackgroundAndLabelledPixels(gfx6, gfx1, results3)
	
	#calculate the fret ratios, removing any ROI with intensity of zero
	FRET =[]
	
	for i in xrange(len(acceptorChIntensity)):
		if (acceptorChIntensity[i]>0) and (donorChIntensity[i]>0):
			#don't write in the zeros to the results
			FRET.append((1000*acceptorChIntensity[i]/donorChIntensity[i]))
	
			table.incrementCounter()
			table.addValue("Frame (Time)", nFrame)
			table.addValue("Label", i)
			table.addValue("Emission ratio", acceptorChIntensity[i]/donorChIntensity[i])

			table.addValue("Mean donor emission", results.getValue("MEAN_INTENSITY",i))
			table.addValue("Mean acceptor emission (FRET)", results2.getValue("MEAN_INTENSITY",i))
			table.addValue("Mean acceptor emission", results3.getValue("MEAN_INTENSITY",i))


			
			table.addValue("Sum donor emission", donorChIntensity[i])
			table.addValue("Sum acceptor emission (FRET)", acceptorChIntensity[i])
			table.addValue("Sum acceptor emission", results3.getValue("SUM_INTENSITY",i))

			
			table.addValue("Volume", cal.pixelWidth * cal.pixelHeight * cal.pixelDepth * results.getValue("PIXEL_COUNT",i))
			table.addValue("Pixel count", results.getValue("PIXEL_COUNT",i))
			table.addValue("x", cal.pixelWidth*results.getValue("CENTROID_X",i))
			table.addValue("y", cal.pixelHeight*results.getValue("CENTROID_Y",i))
			table.addValue("z", cal.pixelDepth*results.getValue("CENTROID_Z",i))
			table.addValue("File name", originalTitle)
		else:
			#must write in the zeros as this array is used to generate the map of emission ratios
			FRET.append(0)
			
	
	
	
	table.show("Results of " + originalTitle)
	
	FRET[0]=0
	FRETarray= array( "f", FRET)
	fp= FloatProcessor(len(FRET), 1, FRETarray, None)
	FRETImp= ImagePlus("FRETImp", fp)
	gfx4=clij2.push(FRETImp)
	clij2.replaceIntensities(gfx1, gfx4, gfx5)
	maxProj=clij2.create(gfx5.getWidth(), gfx5.getHeight(), 1)
	clij2.maximumZProjection(gfx5, maxProj)
	
	
	#pull the images
	
	FRETimp2=clij2.pull(gfx5)
	FRETProjImp=clij2.pull(maxProj)
	labelImp = clij2.pull(gfx1)

	clij2.clear()
	donorImp.close()
	acceptorImp.close()
	acceptorImp2.close()
	
	return table, FRETimp2, FRETProjImp, labelImp


def nearestZProject(imp1):
	relicedImp=Slicer().reslice(imp1)
	relicedStack=relicedImp.getStack()
	width=imp1.getWidth()
	height=imp1.getHeight()
	depth=imp1.getNSlices()
	
	topPixels=zeros('f', width * height)  
	
	stack2=ImageStack( width, height)
	for i in range(1,relicedImp.getNSlices()):
		pixels= relicedStack.getPixels(i)
		for x in xrange(width):
			for pixel in xrange(x, x+width*(depth-1),width):
				#after finding the first pixel above the threshold value, add the value to the list
				if pixels[pixel] != 0:
				
					topPixels[i*width+x]=pixels[pixel]
					#break from looping the y when 1st threshold pixel is found is met -> increases speed drastically! Otherwise need an if statement every loop...
					break
	
	ip2=FloatProcessor(width, height, topPixels, None)
	imp2=ImagePlus("Nearest point proj",ip2)
	imp3= imp2.resize(imp2.getWidth()*2, imp2.getHeight()*2, 'none')
	return imp3



def outline(imp3, originalTitle):
	
	
	#clij implementation -thicker lines
	"""
	src=clij2.push(imp3)
	dst=clij2.create(src)
	dst2=clij2.create(src)
	clij2.detectLabelEdges(src,dst)
	clij2.binaryNot(dst,dst2)
	clij2.multiplyImages(src, dst2, dst)
	imp4=clij2.pull(dst)
	imp4.show()
	clij2.clear()
	"""
	
	imp2=imp3.duplicate()
	stack1=imp3.getStack()
	width=imp3.getWidth()
	height=imp3.getHeight()
	stack2=ImageStack(width, height)
	pixlist=[]
	
	for i in range(imp3.getNSlices()):
		pixlist=[]
		pixels1=stack1.getPixels(i+1)
		#if pixel is different to the pixel to the left or above, set it to 0
		pixels2=map(lambda j: pixels1[j] if pixels1[j]-pixels1[j-1]==0 and pixels1[j]-pixels1[j-width]==0 else 0, xrange(len(pixels1)))
		processor=FloatProcessor(width, height, pixels2, None)
		stack2.addSlice(processor)
	imp2=ImagePlus("Nearest point emission ratios of "+ originalTitle, stack2)
	imp2.show()
	return imp2


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

#get the pixel aspect for use in zscaling kernels for filters
cal = imp1.getCalibration()
pixelAspect=(cal.pixelDepth/cal.pixelWidth)
originalTitle=imp1.getTitle()
#print dir(cal)


IJ.log(originalTitle +" settings:")
IJ.log("segmentChannel, donorChannel, acceptorChannel, acceptorChannel2, thresholdMethod, maxIntensity, gaussianSigma, largeDoGSigma, topHat, topHatSigma, manualSegment, manualThreshold, makeNearProj, dilation, sizeExclude, minSize, maxSize:")
IJ.log(str(options))

segmentChannel, donorChannel, acceptorChannel, acceptorChannel2, thresholdMethod, maxIntensity, gaussianSigma, largeDoGSigma, topHat, topHatSigma, manualSegment, manualThreshold, makeNearProj, dilation, sizeExclude, minSize, maxSize=options
totalFrames=imp1.getNFrames() +1

#table is the final results table
table = ResultsTable()

clij2 = CLIJ2.getInstance()
clij2.clear()



conThresholdStack=ImageStack(imp1.width, imp1.height)
conFRETImp2Stack=ImageStack(imp1.width, imp1.height)
conFRETProjImpStack=ImageStack(imp1.width, imp1.height)
conlabelImpStack=ImageStack(imp1.width, imp1.height)
conNearZStack=ImageStack(imp1.width*2, imp1.height*2)
for nFrame in xrange(1, totalFrames):
	clij2.clear()
	segmentImp=extractChannel(imp1, segmentChannel, nFrame)
	gfx1=clij2.push(segmentImp)
	gfx2=clij2.create(gfx1)
	gfx3=clij2.create(gfx1)
	gfx4=clij2.create(gfx1)
	gfx5=clij2.create(gfx1)
	gfx1,gfx2,gfx3,gfx4,gfx5 = segment(gfx1,gfx2,gfx3,gfx4,gfx5, gaussianSigma, thresholdMethod,maxIntensity, largeDoGSigma, pixelAspect, originalTitle, topHat,topHatSigma, manualSegment, manualThreshold, dilation,sizeExclude, minSize, maxSize)
	
	thresholdImp = clij2.pull(gfx3)
	IJ.setMinAndMax(thresholdImp, 0,1)
	thresholdImp.setCalibration(cal)
	thresholdImp.setTitle("Binary mask of "+originalTitle)
	
	table, FRETimp2, FRETProjImp, labelImp=fretCalculations(imp1, nFrame, donorChannel, acceptorChannel, acceptorChannel2, table, gfx5, gfx2, gfx3, gfx4, gfx1, originalTitle)
	if makeNearProj == True:
		nearZImp = nearestZProject(FRETimp2)
		conNearZStack=concatStacks(conNearZStack,nearZImp)
		nearZImp.close()
		
	#add the images to concatenated stacks
	conThresholdStack = concatStacks(conThresholdStack, thresholdImp)
	conFRETImp2Stack=concatStacks(conFRETImp2Stack, FRETimp2)
	conFRETProjImpStack=concatStacks(conFRETProjImpStack, FRETProjImp)
	conlabelImpStack=concatStacks(conlabelImpStack, labelImp)
	
	thresholdImp.close()
	FRETimp2.close()
	FRETProjImp.close()
	labelImp.close()

#Show the images and make the images pretty... I should have put in a function`

conThresholdImp= ImagePlus( "Threshold image for "+ originalTitle, conThresholdStack)
conThresholdImp.setDimensions(1,  imp1.getNSlices(), imp1.getNFrames())
IJ.setMinAndMax(conThresholdImp, 0,1)
conThresholdImp.setCalibration(cal)
conThresholdImp = CompositeImage(conThresholdImp, CompositeImage.COMPOSITE)
conThresholdImp.show()


conFRETImp2 = ImagePlus( "Emission ratios X1000 of "+ originalTitle, conFRETImp2Stack)
conFRETImp2.setDimensions(1, imp1.getNSlices(), imp1.getNFrames())
conFRETImp2.setCalibration(cal)
stats=StackStatistics(conFRETImp2)
conFRETImp2 = CompositeImage(conFRETImp2, CompositeImage.COMPOSITE)  
IJ.setMinAndMax(conFRETImp2, 0, 4000)
conFRETImp2.show()
IJ.run("16_colors")


conFRETProjImp= ImagePlus( "Max Z  projection of emission ratios X1000 of "+ originalTitle, conFRETProjImpStack)
conFRETProjImp.setDimensions(1, 1, imp1.getNFrames())
conFRETProjImp.setCalibration(cal)
stats=StackStatistics(conFRETProjImp)
IJ.setMinAndMax(conFRETProjImp, 0, 4000)
conFRETProjImp = CompositeImage(conFRETProjImp, CompositeImage.COMPOSITE)  
conFRETProjImp.show()
IJ.run("16_colors")

conlabelImp= ImagePlus("Label map "+ originalTitle, conlabelImpStack)
conlabelImp.setDimensions(1, imp1.getNSlices(), imp1.getNFrames())
conlabelImp.setCalibration(cal)
stats=StackStatistics(conlabelImp)
conlabelImp = CompositeImage(conlabelImp, CompositeImage.COMPOSITE)  
IJ.setMinAndMax(conlabelImp, 0,stats.max)
conlabelImp.show()
IJ.run("glasbey_inverted")


if makeNearProj == True:
	conNearZImp=ImagePlus("Nearest Z proj of  ratios of"+ originalTitle, conNearZStack)
	nearZImpOutlines = outline(conNearZImp,originalTitle)
	cal2=cal.copy()
	cal2.pixelWidth = (cal.pixelWidth/2)
	cal2.pixelHeight =(cal.pixelHeight/2)
	cal2.pixelDepth =( imp1.getNSlices() * cal.pixelDepth)
	nearZImpOutlines.setCalibration(cal2)
	IJ.setMinAndMax(nearZImpOutlines, 0, 4000)
	nearZImpOutlines.show()
	IJ.run("16_colors")
	
	#print cal.getXUnit()


