"""
******************************************************************************************
		Written by Jim Rowe, Alexander Jones' lab (SLCU, Cambridge).
								Started: 2021-11-18		
							 		@BotanicalJim
							james.rowe at slcu.cam.ac.uk
									Version 0.01

Trackmate label image to label map converter

******************************************************************************************
"""


# *******************************import libraries*****************************************
from ij 					import IJ, ImageStack, ImagePlus,CompositeImage
from fiji.util.gui 			import GenericDialogPlus
from ij.process 			import ImageProcessor, StackStatistics, ImageConverter, FloatProcessor
from ij.measure 			import ResultsTable
from array 					import array, zeros
from java.lang 				import Thread
from ij.plugin 				import Slicer
from ij 					import WindowManager as WM  
# *******************************functions************************************************



def selectDialog():
	gd = GenericDialogPlus("Tracks to Labels")
	imps = WM.getImageTitles()
	nonimages=WM.getNonImageTitles()

	if len(imps)>1:
		gd.addChoice("'LblImg_' Trackmate spot image", imps, imps[0])
		gd.addChoice("'Label map' from FRETENATOR", imps, imps[1])
	else:
		gd.addMessage("Not enough images open")

	try:
		gd.addChoice("FRETENTATOR results table", nonimages, nonimages[0])
		fail=0
	except:
		gd.addMessage("No results table open")
		fail=1
	gd.setModal(False)
	gd.showDialog()
	
	while ((not gd.wasCanceled()) and not (gd.wasOKed())):
		Thread.sleep(200)
	if gd.wasCanceled():
		return 1, 0,0,0

	if gd.wasOKed():
		try:
			spotImpName=gd.getNextChoice()
			labelImpName=gd.getNextChoice()
			resultsTableName=gd.getNextChoice()
		except: return 1, 0,0,0			
		return 0, spotImpName, labelImpName, resultsTableName

		
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
	#comp.show()
	return comp

def errorDialog(message):


	gd = GenericDialogPlus("Error")

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

# *******************************BODY of code************************************************

try: 
	from net.haesleinhuepf.clij2 import CLIJ2

except:
	errorDialog("""This plugin requires clij2 to function. 
	
	To install please follow these instructions: 
	
	1. Click Help>Update> Manage update sites
	2. Make sure the "clij" and "clij2" update sites are selected.
	3. Click Close> Apply changes.
	4. Close and reopen ImageJ""")


clij2 = CLIJ2.getInstance()
clij2.clear()

cancelled, spotImpName, labelImpName, resultsTableName =selectDialog()
if cancelled != 1:
	rt = ResultsTable.getResultsTable(resultsTableName).clone()
	spotImp=WM.getImage(spotImpName)
	labelImp=WM.getImage(labelImpName)
	if spotImp.getNFrames()<2:
		errorDialog(spotImpName+' is not a time series image')
	if labelImp.getNFrames()<2:
		errorDialog(labelImpName+' is not a time series image')
	if (spotImp.getHeight() != labelImp.getHeight() or
	spotImp.getWidth()!= labelImp.getWidth() or
	spotImp.getStackSize()!= labelImp.getStackSize() or
	spotImp.getNFrames()!= labelImp.getNFrames()):
		errorDialog('Images are not of the same dimensions')
	results=ResultsTable()
	conTrackStack=ImageStack(spotImp.width, spotImp.height)
	concatLabels=[]
	concatTrackSpot=[]
	
	for nFrame in xrange(1, spotImp.getNFrames()+1 ):
		spotImpF = extractFrame(spotImp, nFrame)
		labelImpF = extractFrame(labelImp, nFrame)
		clij2.clear()
		spotGfx=clij2.push(spotImpF)
		labelGfx=clij2.push(labelImpF)
		results2=ResultsTable()
		
		clij2.statisticsOfBackgroundAndLabelledPixels(spotGfx,labelGfx, results2)
		
		identifiers=results2.getColumn(0)
			
		trackSpot=results2.getColumn(13)
		trackSpotWithBackgrounds=results2.getColumn(13)
		trackSpotWithBackgrounds[0]=0
		trackArray= array( "f", trackSpotWithBackgrounds)
		fp= FloatProcessor(len(trackSpotWithBackgrounds), 1, trackArray, None)
		TrackImp= ImagePlus("TrackImp", fp)
		#TrackImp.show()
		gfx3=clij2.push(TrackImp)
		gfx5=clij2.create(labelGfx)
		clij2.replaceIntensities(labelGfx, gfx3, gfx5)
		trackedImp=clij2.pull(gfx5)
		conTrackStack=concatStacks(conTrackStack, trackedImp)
		#trackedImp.show()
		#print nFrame
		
		for i in range(len(identifiers)):

			

				concatLabels.append(identifiers[i])
				concatTrackSpot.append(trackSpot[i])

	conTrackImp= ImagePlus("Tracked "+labelImpName, conTrackStack)
	conTrackImp.setDimensions(1, spotImp.getNSlices(), spotImp.getNFrames())
	cal = labelImp.getCalibration()
	conTrackImp.setCalibration(cal)
	stats=StackStatistics(conTrackImp)
	conTrackImp = CompositeImage(conTrackImp, CompositeImage.COMPOSITE)  
	IJ.setMinAndMax(conTrackImp, 0,stats.max)
	conTrackImp.show()
		
	
	for i in range(len(concatLabels)):

		try:
			rt.setValue("TrackID", i,concatTrackSpot[i])
			rt.setValue("Label value",i, concatLabels[i])
		except:
			print "nope"+str(i)
	rt.show('Tracked '+ resultsTableName)
	IJ.run("glasbey_inverted")