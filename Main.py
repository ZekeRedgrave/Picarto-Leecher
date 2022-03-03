import sys, psutil, os, json, threading, math

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import ffmpeg, requests

from API import *
# MView - Main Area
class MView(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		self.MView_Urlbox = QLineEdit(placeholderText="Ex. https://picarto.tv/<Channel Name>/videos/<Video ID>")
		#self.MView_Urlbox.setPlaceholder("Ex. https://picarto.tv/<Channel Name>/videos/<Video ID>")
		MView_UrlButton = QPushButton("Go!")
		MView_UrlButton.clicked.connect(self.MView_UrlClicked)

		MView_HL1 = QHBoxLayout()
		MView_HL1.setContentsMargins(10,10,10,10)
		MView_HL1.addWidget(self.MView_Urlbox)
		MView_HL1.addWidget(MView_UrlButton)
		# MView - Loader Area
		self._MView_LoaderArea = MView_LoaderArea()
		MView_VL1 = QVBoxLayout()
		MView_VL1.setContentsMargins(0,0,0,0)
		MView_VL1.setSpacing(0)
		MView_VL1.addLayout(MView_HL1)
		MView_VL1.addWidget(self._MView_LoaderArea)
		#-------------------------------------------------------------
		# Almost Done
		#-------------------------------------------------------------

		self.setLayout(MView_VL1)
	#-------------------------------------------------------------
	# Main - Events
	#-------------------------------------------------------------
	# View
	def MView_UrlClicked(self):
		if self.MView_Urlbox.text() != "": 
			self._MView_LoaderArea.load(self.MView_Urlbox.text())
			self.MView_Urlbox.setText("")
		else: QMessageBox.about(self, "Picarto-Leecher - Error", "Description: Blank Detected\nWhere: Url Linebox")
# MView - Loader Area
class MView_LoaderArea(QScrollArea):
	def __init__(self):
		QScrollArea.__init__(self)

		self.MView_LoaderLayout = QVBoxLayout()
		self.MView_LoaderLayout.setAlignment(Qt.AlignTop)

		MView_VL2 = QVBoxLayout()
		MView_VL2.addLayout(self.MView_LoaderLayout)
		MView_VL2.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
		
		MView_W1 = QWidget()
		MView_W1.setLayout(MView_VL2)		
		#-------------------------------------------------------------
		# Almost Done
		#-------------------------------------------------------------
		# Threading
		self.DownloadTP = QThreadPool()
		self.ConstructTP = QThreadPool()
		self.getCount = 0

		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setWidget(MView_W1)

	def load(self, url=""):
		self.PreparingThread = MView_DownloadRunnable(url, self.getCount)
		self.PreparingThread.Signal.itemLoader.connect(self.MView_LoaderItem)
		self.PreparingThread.Signal.itemStatus.connect(self.MView_Status)
		self.PreparingThread.Signal.itemProgress.connect(self.MView_Progress)
		self.PreparingThread.Signal.itemFinished.connect(self.MView_Finish)
		self.DownloadTP.start(self.PreparingThread)

	def MView_LoaderItem(self, getJSON):
		# Load Item
		if getJSON["MViewLT"] == 1:
			tempImageLabel = QLabel("No Image")
			tempImageLabel.setMinimumHeight(128)
			tempImageLabel.setMaximumHeight(128)
			tempImageLabel.setMinimumWidth(128)
			tempImageLabel.setMaximumWidth(128)
			tempImageLabel.setWordWrap(True)
			tempImageLabel.setAlignment(Qt.AlignCenter)
			tempImageLabel.setObjectName("MView_LoaderImageID"+ str(self.getCount))
			tempImageLabel.setStyleSheet("background-color: transparent; border: 1px solid grey;")

			tempVL1 = QVBoxLayout()
			tempVL1.addWidget(tempImageLabel)
			tempVL1.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

			tempTitleLabel = QLabel("No Title")
			tempTitleLabel.setWordWrap(True)
			tempTitleLabel.setObjectName("MView_LoaderTitleID"+ str(self.getCount))
			tempDirectoryLabel = QLabel("No Files Existed Yet!")
			tempDirectoryLabel.setWordWrap(True)
			tempDirectoryLabel.setObjectName("MView_LoaderDirectoryID"+ str(self.getCount))
			tempProgressBar = QProgressBar()
			# tempProgressBar.setMinimumHeight(8)
			# tempProgressBar.setMaximumHeight(8)
			tempProgressBar.setObjectName("MView_LoaderProgressID"+ str(self.getCount))
			tempStatusLabel = QLabel("")
			tempStatusLabel.setWordWrap(True)
			tempStatusLabel.setObjectName("MView_LoaderStatusID"+ str(self.getCount))

			tempVL2 = QVBoxLayout()
			tempVL2.addWidget(tempTitleLabel)
			tempVL2.addWidget(tempDirectoryLabel)
			tempVL2.addWidget(tempProgressBar)
			tempVL2.addItem(QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Minimum))
			tempVL2.addWidget(tempStatusLabel)
			tempVL2.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

			tempH1 = QHBoxLayout()
			tempH1.addLayout(tempVL1)
			tempH1.addLayout(tempVL2)

			tempW1 = QWidget()
			tempW1.setObjectName("MView_LoaderWidgetID"+ str(self.getCount))
			tempW1.setStyleSheet("#MView_LoaderWidgetID" +str(self.getCount)+ " { border-bottom: 1px solid grey; }")
			tempW1.setMinimumHeight(150)
			tempW1.setMaximumHeight(150)
			tempW1.setLayout(tempH1)

			self.MView_LoaderLayout.addWidget(tempW1)
			self.getCount += 1
		# Load Display Information
		if getJSON["MViewLT"] == 2:
			tempImageLabel = self.findChild(QLabel, "MView_LoaderImageID"+ str(getJSON["MViewID"]))
			getImage = QImage()
			getImage.loadFromData(getCover(getJSON["MViewCover"]))
			tempPixmap = QPixmap(getImage)
			tempImageLabel.setPixmap(tempPixmap.scaled(tempImageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

			tempTitleLabel = self.findChild(QLabel, "MView_LoaderTitleID"+ str(getJSON["MViewID"]))
			tempTitleLabel.setText("Title: ({})[{}] - {}".format(getJSON["MViewChannel"], getJSON["MViewUID"], getJSON["MViewTitle"]))

			tempDirectoryLabel = self.findChild(QLabel, "MView_LoaderDirectoryID"+ str(getJSON["MViewID"]))
			tempDirectoryLabel.setText("Path Directory: "+ getJSON["MViewPath"])

			tempProgressBar = self.findChild(QProgressBar, "MView_LoaderProgressID"+ str(getJSON["MViewID"]))
			tempProgressBar.setMaximum(getJSON["MViewSize"])

	def MView_Status(self, getJSON):
		tempStatusLabel = self.findChild(QLabel, "MView_LoaderStatusID"+ str(getJSON["MViewID"]))
		if getJSON["isError"]: 
			tempStatusLabel.setText(getJSON["ErrorSummary"])
			tempStatusLabel.setStyleSheet("color: red")

		else: tempStatusLabel.setText(getJSON["MViewStatus"])

	def MView_Progress(self, getJSON):
		tempProgressBar = self.findChild(QProgressBar, "MView_LoaderProgressID"+ str(getJSON["MViewID"]))
		tempProgressBar.setValue(getJSON["MViewSV"])

	def MView_Finish(self, getJSON):
		self.PreparingThread = MView_ConstructRunnable(getJSON["MViewID"], getJSON["MViewTitle"], getJSON["MViewPath"])
		self.PreparingThread.Signal.itemStatus.connect(self.MView_Status)
		self.DownloadTP.start(self.PreparingThread)
# Main - Threading
class MView_DownloadRunnable(QRunnable):
	def __init__(self, Url,ID):
		QRunnable.__init__(self)

		self.Url = Url
		self.ID = ID
		self.Signal = MView_DownloadObject()
		# -----------------------------------------
		self.FSSize = 0
		self.FSValue = 0
		self.FSMV = 0
		# "title": <filename of ts extension file>
		# "path": <where the files saved in the dir>
		# "isError": <set true if there is an error>,
		# "isChecked": <set to true if the file is done downloaded with correct filesize_max matched> # not availabled this version yet
		self.FSList = {}

	def run(self):
		# Create Dynamic Widget
		self.Signal.itemLoader.emit({ "MViewLT": 1 })
		# Sending Status
		self.Signal.itemStatus.emit({
			"MViewID": self.ID,
			"MViewStatus": "Fetching information from "+ self.Url +" to your Computer",
			"isError": False,
			"ErrorSummary": ""
		})
		# Get Information
		_getInfo = getInfo(self.Url)
		if _getInfo["isError"] is False: 
			rawInfo = _getInfo["Information"]
			pathDir = FileSystem().getPath+ "/Download/({})[{}] - {}".format(rawInfo["channel"], rawInfo["id"], rawInfo["title"])
			# Send Info to GUI for New Info Update
			self.Signal.itemLoader.emit({
				"MViewLT": 2,
				"MViewID": self.ID,
				"MViewCover": rawInfo["thumbnails"]["web"],
				"MViewTitle": rawInfo["title"],
				"MViewChannel": rawInfo["channel"],
				"MViewUID": rawInfo["id"],
				"MViewPath": pathDir,
				"MViewSize": rawInfo["filesize"]
			})
			self.Signal.itemStatus.emit({
				"MViewID": self.ID,
				"MViewStatus": "Fetching Playlist from "+ rawInfo["file"] +" to your Computer",
				"isError": False,
				"ErrorSummary": ""
			})
			# Create Directory
			if os.path.isdir(pathDir) is False: os.makedirs(pathDir)
			# Get Playlist
			_getPlaylist = self.runPlaylist(rawInfo["file"])
			if _getPlaylist != None:
				self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"MViewStatus": "Preparing for Multi-Threading",
					"isError": False,
					"ErrorSummary": ""
				})
				# Preparing for Multi-Threading
				prepareThread = []
				tempThread = []
				getCount = 1
				_FSMaxList = len(str(len(_getPlaylist["Listm3u8"])))
				#getMax = psutil.cpu_count(logical=True)
				getMax = FileSystem().getThreadingMax()

				test = 0
				for x in _getPlaylist["Listm3u8"]:
					# self.FSList.update({
					# 	x["title"]: {
					# 		"path": pathDir+ "/" +x["title"],
					# 		"isError": False,
					# 		"isChecked": False
					# 	}
					# })

					tempThread.append(threading.Thread(target=self.runDownload, args=(x["url"], "{}.ts".format(str(self.FSMV).zfill(_FSMaxList)), pathDir)))

					if getCount == getMax:
						prepareThread.append(tempThread)
						self.FSMV += 1
						# Reset
						tempThread = []
						getCount = 1

						#if test == 2: break
						#test += 1

					else: 
						getCount += 1
						self.FSMV += 1

				# Ready
				self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"MViewStatus": "Ready",
					"isError": False,
					"ErrorSummary": ""
				})
				# Start
				for x in prepareThread:
					for y in x: y.start()
					for y in x: y.join()
				# Finished
				os.system("clear")
				print("FS Value: {}".format(self.FSValue))
				print("FS MV: {}".format(self.FSMV))
				if self.FSMV == self.FSValue: self.Signal.itemFinished.emit({
					"MViewID": self.ID,
					"MViewTitle": rawInfo["title"],
					"MViewPath": pathDir,
					"MViewStatus": "Preparing for Merging All Multiple Files into Single Files!",
					"ErrorSummary": "",
					"isError": False
				})
				else: self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"MViewStatus": "",
					"isError": True,
					"ErrorSummary": "There is some files aren't downloaded. Redownload Again!s"
				})

		else: self.Signal.itemStatus.emit({
			"MViewID": self.ID,
			"isError": True,
			"ErrorSummary": _getInfo["ErrorSummary"]
		})

	def runPlaylist(self, url=""):
		_getPlaylist = getPlaylist(url)

		if _getPlaylist["isError"] is False:
			self.Signal.itemStatus.emit({
				"MViewID": self.ID,
				"MViewStatus": "Preparing to Download All Video Fragments from Picarto Server to your Computer",
				"isError": False,
				"ErrorSummary": ""
			})

			return _getPlaylist
		else: 
			self.Signal.itemStatus.emit({
				"MViewID": self.ID,
				"isError": True,
				"ErrorSummary": _getPlaylist["ErrorSummary"]
			})

			return None

	def runDownload(self, url="", title="", path="", retry=0):
		try:
			with requests.get(url, headers=FileSystem().getHeader(), stream=True) as r, open(path+ "/" +title, "wb") as f, tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=len(requests.get(url, headers=FileSystem().getHeader(), stream=True).content), file=sys.stdout, desc=title) as p:
				for x in r.iter_content(chunk_size=1024):
					ds = f.write(x)
					p.update(ds)

			self.FSValue += 1
			self.FSSize += len(open(path+ "/" +title, "rb+").read())
			self.Signal.itemProgress.emit({
				"MViewID": self.ID,
				"MViewSV": self.FSSize
			})
			self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"MViewStatus": "Downloading......... {} - {} File Completion".format(self.FSValue, self.FSMV),
					"isError": False,
					"ErrorSummary": ""
				})
			# self.FSList[title]["isChecked"] = True
			# self.FSList[title]["isError"] = False

		except Exception as e:
			if retry == FileSystem().getRetry():
				# No Recursive Loop
				self.FSValue -= 1
				self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"isError": True,
					"ErrorSummary": _str(e)
				})
				self.Signal.itemStatus.emit({
					"MViewID": self.ID,
					"MViewStatus": "Downloading......... {} - {} File Completion".format(self.FSValue, self.FSMV),
					"isError": False,
					"ErrorSummary": ""
				})
				# self.FSList[title]["isChecked"] = False
				# self.FSList[title]["isError"] = True

			else: 
				time.sleep(1) # Take a rest for a second
				self.runDownload(url, path, retry + 1) # Recursive Loop


class MView_DownloadObject(QObject):
	itemUrl = pyqtSignal(str)
	itemLoader = pyqtSignal(dict)
	itemDownload = pyqtSignal(dict)
	itemStatus = pyqtSignal(dict)
	itemProgress = pyqtSignal(dict)
	itemFinished = pyqtSignal(dict)

class MView_ConstructRunnable(QRunnable):
	def __init__(self, ID, title="", path=""):
		QRunnable.__init__(self)

		self.ID = ID
		self.FSTitle = title
		self.FSPath = path
		self.FSValueLevel = 0
		self.FSMaxLevel = 0
		self.Signal = MView_ConstructObject()

	def run(self):
		files = []
		for x in os.listdir(self.FSPath):
			if os.path.splitext(x)[1] == ".ts" or os.path.splitext(x)[1] == ".mkv":
				if len(open(self.FSPath+ "/" + x, "rb+").read()) != 0:	files.append(self.FSPath+ "/" +str(int(os.path.splitext(x)[0])).zfill(5) + os.path.splitext(x)[1])

		files.sort() # Sorting all the files but naming is kinda stucked out there
		self.getLevel(len(files))

		for x in range(self.FSMaxLevel):
			self.Signal.itemStatus.emit({
				"MViewID": self.ID,
				"isError": False,
				"MViewStatus": "Merging......... {} - {} File Completion".format(self.FSValueLevel, self.FSMaxLevel),
				"ErrorSummary": ""
			})
			self.processing("output "+ str(x).zfill(5), self.FSPath)
			for x1 in range(5):
				print(x1)
				time.sleep(1)

			self.FSValueLevel += 1

		self.clean()
		self.Signal.itemStatus.emit({
				"MViewID": self.ID,
				"isError": False,
				"MViewStatus": "Done!",
				"ErrorSummary": ""
			})

	def clean(self):
		files = []
		for x in os.listdir(self.FSPath):
			if os.path.splitext(x)[1] == ".txt":
				if len(open(self.FSPath+ "/" + x, "rb+").read()) != 0:	files.append(self.FSPath+ "/" +x)

		for x in files:
			if os.path.exists(x): os.remove(x)

	def getLevel(self, x):
		x2 = math.ceil(x / psutil.cpu_count(logical=True))

		if math.ceil(x) == 1: pass
		else:
			self.FSMaxLevel += 1 
			self.getLevel(x2)

	def processing(self, output="", path=""):
		files = []
		fileCount = 0
		for x in os.listdir(path):
			if os.path.splitext(x)[1] == ".ts" or os.path.splitext(x)[1] == ".mkv":
				if len(open(self.FSPath+ "/" + x, "rb+").read()) != 0:	files.append(self.FSPath+ "/" +x)

		files.sort()

		x = math.ceil(len(files) / psutil.cpu_count(logical=True))
		prepareThread = []
		prepareCount = 0
		for x1 in range(x):
			tempFile = []

			for x2 in range(psutil.cpu_count(logical=True)):
				try:
					tempFile.append(files[fileCount])
					fileCount += 1
				except Exception as e: pass
				
			prepareThread.append(threading.Thread(target=self.constructVideo, args=(tempFile, output, prepareCount) ))
			prepareCount += 1
		# print(prepareThread)
		for x1 in prepareThread: x1.start()
		for x1 in prepareThread: x1.join()
		for x1 in files: os.remove(x1)

	def constructVideo(self, files=[], name="", count=0):
		a = VideoFileMerger()
		for a1 in files: a.insertVideo(a1)

		a.run("{} - {}".format(name, str(count).zfill(5)), self.FSPath)

class MView_ConstructObject(QObject):
	itemFiles = pyqtSignal(dict)
	itemStatus = pyqtSignal(dict)
	itemFinished = pyqtSignal(dict)
	itemError = pyqtSignal(dict)
if __name__ == '__main__':
	App = QApplication(sys.argv)

	x = MView()
	x.setWindowTitle("Picarto Leecher v0.2_20220303.snapshot by Zeke S. Redgrave")
	x.setMinimumWidth(540)
	x.setMinimumHeight(480)
	x.setContentsMargins(0, 0, 0, 0)
	# x.showMaximized()
	x.resize(540, 700)
	x.show()

	sys.exit(App.exec_())

