"""
******************************************************************************************
		Written by Jim Rowe, Alexander Jones' lab (SLCU, Cambridge).
								Started: 2021-01-30	
							 		@BotanicalJim
							james.rowe at slcu.cam.ac.uk
									Version 0.7

******************************************************************************************
"""


# *******************************import libraries*****************************************

from ij 					import IJ, ImagePlus, ImageStack
from fiji.util.gui 			import GenericDialogPlus
from ij 					import WindowManager as WM  
from java.awt.event 		import ActionListener,AdjustmentListener, ItemListener
from net.haesleinhuepf.clij2 import CLIJ2
from ij.process 			import ImageProcessor, ShortProcessor,StackStatistics, ImageConverter
from java.awt  				import GridLayout, Font, Color
from ij.measure 			import ResultsTable
from ij.gui 				import Overlay
from ij.gui 				import TextRoi, Roi



# *******************************classes*****************************************



class previewLabelerAndListeners(ActionListener, AdjustmentListener):
	'''Class which unique function is to handle the button clics'''
	def __init__(self, labelPreviewImp, maxZPreviewImp, maxYPreviewImp, src,results,identifiers,nucLoc,zs, slider1,slider2, gd):

		"""labelPreviewImp -  label image preview; maxZPreviewImp - maxZ label preview; maxYPreviewImp - maxY label preview"""
		self.labelPreviewImp=labelPreviewImp
		self.maxZPreviewImp=maxZPreviewImp
		self.maxYPreviewImp=maxYPreviewImp
		self.src=src
		self.results=results
		self.identifiers=identifiers
		self.nucLoc=nucLoc
		self.zs=zs
		self.slider1=slider1
		self.slider2=slider2
		self.gd=gd
		self.current=self.labelPreviewImp.getCurrentSlice()
		
		
		
	def renderPreview(self):
		try:
			self.labelPreviewImp.close()
			self.maxZPreviewImp.close()
			self.maxYPreviewImp.close()
		except:
			print "imps already closed"
		
		
		fp= ShortProcessor(len(labelValues), 1, labelValues, None)
		labelerImp= ImagePlus("labeler", fp)
		src2=clij2.push(labelerImp)
		dst=clij2.create(src)
		labelerImp.close()
		
		clij2.replaceIntensities(self.src, src2, dst)
		self.labelPreviewImp=clij2.pull(dst)
		previewDisplaySettings(self.labelPreviewImp, "label preview", 100)
		self.labelPreviewImp.setSlice(self.current)

		dst2=clij2.create( width, height, 1)
		clij2.maximumZProjection(dst,dst2)
		self.maxZPreviewImp=clij2.pull(dst2)
		previewDisplaySettings(self.maxZPreviewImp, "maxZ label preview", 50)
		
		dst3=clij2.create( width, depth, 1)
		clij2.maximumYProjection(dst,dst3)
		self.maxYPreviewImp=clij2.pull(dst3)
		previewDisplaySettings(self.maxYPreviewImp, "maxY label preview", 50)
		
		
		dst3.close()
		dst.close()
		dst2.close()
		src2.close()


		labelWindow = self.labelPreviewImp.getWindow()
		x=labelWindow.getLocation().x
		y=labelWindow.getLocation().y
		
		maxZPreviewWindow=self.maxZPreviewImp.getWindow()
		maxZPreviewWindow.setLocation(x, y+height+50)
		maxYPreviewWindow=self.maxYPreviewImp.getWindow()
		maxYPreviewWindow.setLocation(x+width/2, y+height+50)
		print labelWindow
	def actionPerformed(self, event): 
		"""event: actionlistener does stuff on buttonpress"""


		Source = event.getSource() # returns the Button object
		self.current=self.labelPreviewImp.getCurrentSlice()
		
		if Source.label == "Set top":
			self.top = self.labelPreviewImp.getCurrentSlice()
			self.bottom = self.slider2.getValue()
			self.slider1.setValue(int(self.top))
			if (self.bottom < self.top) :
				self.bottom=self.top
				self.slider2.setValue(int(self.top))
			return
			
		if Source.label == "Set bottom":
			self.top = self.slider1.getValue()
			self.bottom = self.labelPreviewImp.getCurrentSlice()
			self.slider2.setValue(int(self.bottom))
			if self.bottom < self.top:
				self.slider1.setValue(int(self.bottom))
				self.top = self.bottom
				print "B"
			return
			
		if Source.label == "Whole stack":
			self.top = 1
			self.bottom = depth
			self.slider1.setValue(int(self.top))
			self.slider2.setValue(int(self.bottom))
			return
			
		if Source.label == "Just slice":
			print "current slice"
			self.top = self.labelPreviewImp.getCurrentSlice()
			self.bottom = self.labelPreviewImp.getCurrentSlice()
			self.slider2.setValue(int(self.top))
			self.slider1.setValue(int(self.bottom))
			return
		
		if Source.label[:5]=="label":
			[int(s) for s in Source.label.split() if s.isdigit()]
			s=int(s)
			#try:
			roi1 = self.labelPreviewImp.getRoi()
			selectedPixels=roi1.getContainedPoints()
			roiPixelLoc= map(lambda i : i.y * width +i.x, selectedPixels)
	
			pixels2=filter(lambda i: nucLoc[i] in roiPixelLoc, xrange(len(nucLoc)))

			#on first run set self.top and self.bottom to top and bottom of the stack
			try: print self.top
			except:  self.top=1
			try: print self.bottom
			except: self.bottom=labelPreviewImp.getNSlices()
			choice= self.gd.getChoices().get(0)

			if choice.getSelectedItem()== "Slice":
				top=self.current
				bottom=self.current
			else:
				top=self.top
				bottom=self.bottom
			
			pixels2=filter(lambda i :max(bbze[i],bottom)-min(top,bbz[i]) <= (bbze[i]-bbz[i])+ (bottom-top),pixels2)
			nucleiLabels=map(lambda i : i+1,pixels2)

			#print(map(lambda i:self.zs[i], pixels2))
			#print len(pixels2)

			
			labelDict[s] =nucleiLabels+labelDict[s]
			labelDict[s] =sorted(list(set(labelDict[s])))
			
			
			for key in labelDict:
				if key != s :
					labelDict[key]=filter(lambda x: x not in labelDict[s], labelDict[key])
			#print labelDict
			for key in labelDict:
				for value in labelDict[int(key)]:
					labelValues[value]=int(key)
			labelValues[0]=0
		self.renderPreview()
		
		#except:
		#	print "No roi"
		return
		# Do an action depending on the button clicked
	def adjustmentValueChanged(self, event):  
		""" event: an AdjustmentEvent with data on the state of the scroll bar. """ 

		 #return if the user is still dragging
		 
		if event.getValueIsAdjusting():
			return
		Source = event.getSource()
		
		try: self.slider1=self.gd.getSliders().get(0)
		except: print "huh?"
		try: self.slider2=self.gd.getSliders().get(1)
		except: print "huh?2"
		
		self.top = self.slider1.getValue()
		self.bottom = self.slider2.getValue()

		#make top and bottom sliders autocorrect for each other
		if Source== self.slider1:
			if self.top > self.bottom:
				self.slider2.setValue(int(self.top))
				self.bottom=self.top
				print "A"
		if Source== self.slider2:		
			if self.bottom < self.top:
				self.slider1.setValue(int(self.bottom))
				self.top = self.bottom
				print "B"


# *******************************functions************************************************

def previewDisplaySettings(image, title, zoom):
	"""Apply wanted settings for previews"""
	ImageConverter(image).convertToGray16()
	image.show()
	IJ.setMinAndMax(image, 0, 255)
	IJ.run("glasbey_on_dark")
	image.setTitle(title)
	IJ.run("Set... ", "zoom="+str(zoom))


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
		
def dialog(imp1, labelPreviewImp,maxZPreviewImp,maxYPreviewImp, src, results,identifiers,nucLoc,zs, labelColorBarImp):
	gd = GenericDialogPlus("ROI labeller")
	categories=11

	#placeholder slider variables so the class can be initiated
	slider1=0
	slider2=0
	test=previewLabelerAndListeners(labelPreviewImp, maxZPreviewImp, maxYPreviewImp, src, results,identifiers,nucLoc,zs, slider1,slider2, gd)
	

	for i in range(1,categories):
		gd.addButton("label "+str(i), test)
		
	gd.addImage(labelColorBarImp)
	#imp7.close() - causes an error as image needed for the dialog
	gd.addButton("Set top",test)
	gd.addButton("Whole stack",test)
	gd.addButton("Set bottom", test)
	

	
	gd.addSlider("Top",1, imp1.getStackSize(), 1)
	gd.addSlider("Bottom",1, imp1.getStackSize(),imp1.getStackSize())
	slider1=gd.getSliders().get(0)
	slider2=gd.getSliders().get(1)
	test.slider1=slider1
	test.slider2=slider2
	slider1.addAdjustmentListener(test)  
	slider2.addAdjustmentListener(test)
	gd.addChoice("Apply labeling to:", ["(Sub)stack", "Slice"], "(Sub)stack")
	
	gd.setLayout(GridLayout(0,2))
	
	gd.setModal(False)
	buttons=gd.getButtons()
	
	gd.showDialog()


def createLabelColorBar():

	imp7 = ImagePlus("labelColorBar", ShortProcessor(180, 20))
	ip7 = imp7.getProcessor()
	pix=ip7.getPixels()
	n_pixels = len(pix)
	# catch width
	w = imp7.getWidth()
	# create a ramp gradient from left to right
	for i in range(len(pix)):
		pix[i] = int((i % w)/18)+1
		
	# adjust min and max
	ip7.setMinAndMax(0, 255)
	font = Font("SansSerif", Font.PLAIN, 12)
	overlay = Overlay()
	for i in range(len(pix)):
		
		roi = TextRoi(i*18+2, 2, str(i+1), font)
		roi.setStrokeColor(Color.black)
		overlay.add(roi)
		imp7.setOverlay(overlay)
	
	imp7.show()
	IJ.run("glasbey_on_dark")
	imp7=imp7.flatten()

	return imp7

# *****************************body of code starts****************************************


clij2 = CLIJ2.getInstance()
clij2.clear()

imp1=IJ.getImage()
height=imp1.getHeight()
width=imp1.getWidth()
depth=imp1.getStackSize()

stats=StackStatistics(imp1)
nucleiLabels=[]
src=clij2.push(imp1)

size=stats.max
labelValues=[1]*int(size+1)
labelValues[0]=0

fp= ShortProcessor(len(labelValues), 1, labelValues, None)
labelerImp= ImagePlus("labeler", fp)
src2=clij2.push(labelerImp)
dst= clij2.create(src)
clij2.replaceIntensities(src, src2, dst)

results=ResultsTable()

labelPreviewImp=clij2.pull(dst)
ImageConverter.setDoScaling(0)
previewDisplaySettings(labelPreviewImp, "label preview", 100)
clij2.statisticsOfLabelledPixels(dst, src, results)
#results.show("reslets")

dst2=clij2.create( width, height, 1)
clij2.maximumZProjection(dst, dst2)
maxZPreviewImp=clij2.pull(dst2)
previewDisplaySettings(maxZPreviewImp, "maxZ label preview", 50)

dst3=clij2.create( width, depth, 1)
clij2.maximumYProjection(dst,dst3)
maxYPreviewImp=clij2.pull(dst3)
previewDisplaySettings(maxYPreviewImp, "maxY label preview", 50)

labelWindow = labelPreviewImp.getWindow()
x=labelWindow.getLocation().x
y=labelWindow.getLocation().y

maxZPreviewWindow=maxZPreviewImp.getWindow()
maxZPreviewWindow.setLocation(x, y+height+50)
maxYPreviewWindow=maxYPreviewImp.getWindow()
maxYPreviewWindow.setLocation(x+width/2, y+height+50)


dst.close()
dst2.close()
src2.close()
dst3.close()

labelDict={1:sorted(nucleiLabels), 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[]}

identifiers=[]
xs=[]
ys=[]
zs=[]
bbz=[]
bbze=[]
for i in range(int(size)):
	try:
		
		xs.append(int(results.getValue("CENTROID_X",i)))
		ys.append(int(results.getValue("CENTROID_Y",i)))
		zs.append(int(results.getValue("CENTROID_Z",i)))
		bbz.append(results.getValue("BOUNDING_BOX_Z",i)+1)
		bbze.append(results.getValue("BOUNDING_BOX_END_Z",i)+1)
		identifiers.append(results.getValue("IDENTIFIER", i))
	except:
		identifiers.append(results.getValue("IDENTIFIER", i))
		xs.append(int(width/2))
		ys.append(int(height/2))
		zs.append(int(depth/2))
		bbz.append(1)
		bbze.append(1)

nucLoc= map(lambda i : ys[i] * width +xs[i], range(len(xs)))

labelColorBarImp= createLabelColorBar()

#print dir(WM)
dialog(imp1, labelPreviewImp, maxZPreviewImp, maxYPreviewImp, src, results, identifiers,nucLoc,zs, labelColorBarImp)
