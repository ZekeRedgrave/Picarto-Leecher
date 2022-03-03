import sys, os, json, threading, time, math
import tqdm, ffmpeg, requests, m3u8, psutil

class FileSystem():
	def __init__(self):
		self.getPath = os.path.dirname(os.path.realpath(__file__))
		self.getJSON = self.getDB()

		if os.path.isdir(self.getPath+ "/Temp") is False: os.makedirs(self.getPath+ "/Temp")
		if os.path.isdir(self.getPath+ "/Download") is False: os.makedirs(self.getPath+ "/Download")
		# self.getJSON["FileSystem"]["getIcon"] = self.getPath+ "/Icons/2x/"

		if os.path.isfile(self.getPath+ "/Config.json") is False:
			open(self.getPath+ "/Config.json", "w+").write(json.dumps({
				"Directory": {
					"Download": self.getPath+ "/Download",
					"Temp": self.getPath+ "/Temp"
				},
				"System": {
					"ThreadingMax": "",
					"isCustomThreadingMax": False
				},
				"CentralisedNetwork": {
					"Header": {
						"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
						"Accept-Encoding": "gzip, deflate, sdch",
				    	"Accept-Language": "en-US,en;q=0.8",
						"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
					},
					"Server": "https://api.picarto.tv/api/v1",
					"Retry": 5
				},
				"Account": {
					"Username": "",
					"Password": ""
				}
			}, indent=4))
	# Get Full Icon Image Path
	def getIcon(self, name): return QIcon(self.getJSON["FileSystem"]["getIcon"]+ name)
	def getHeader(self): return self.getDB()["CentralisedNetwork"]["Header"]
	def getRetry(self): return self.getDB()["CentralisedNetwork"]["Retry"]
	# Other
	def getDB(self): return json.loads(open(self.getPath+ "/Config.json", "r+").read())
	def setDB(self, getJSON): 
		tempJSON = getJSON
		tempJSON.update()

		open(self.getPath+ "/Config.json", "w+").write(json.dumps(tempJSON, indent=4))
	# -------------------------------------------------------------------------------------------------------
	def getThreadingMax(self):
		x = self.getDB()
		_x = psutil.cpu_count(logical=True)
		if str(x["System"]["ThreadingMax"]) != "": 
			if int(x["System"]["ThreadingMax"]) == _x: pass
			else: 
				x["System"]["isCustomThreadingMax"] = True
				self.setDB(x)

		else:
			x["System"]["ThreadingMax"] = _x
			x["System"]["isCustomThreadingMax"] = False

			self.setDB(x)

		print(x)

		return int(x["System"]["ThreadingMax"])

class VideoFileMerger():
	def __init__(self, tempName="", path=""):
		
		self.FSText = ""
		# ------------------------------------------
		if path != "": self.insertVideo(path)

	def insertVideo(self, path=""):
		if path != "": self.FSText += "file '{}'\n".format(path)

	def run(self, name="", path=""):
		# Save as temp txt file
		open("{}/{}.txt".format(path, name), "w+").write(self.FSText)
		# Trying to Merge all chunk of videos into single file
		try:
			if self.FSText != "": ffmpeg.input("{}/{}.txt".format(path, name), f="concat", safe=0).output("{}/{}.mkv".format(path, name), c="copy").run()

			return {
				"isError": False,
				"ErrorSummary": "",
				"Filename": name,
				"FilePath": path+ "/" +name
			}

		except Exception as e: return {
			"isError": True,
			"ErrorSummary": e,
			"Filename": name,
			"FilePath": ""
		}

def getInfo(url=""):
	# Preparing
	getJSON = None
	getChannel = url.split("/")[3]
	getVideoID = url.split("/")[5]
	isExist = False
	# Contacting The Info via API	
	try:
		getRequest = requests.get("https://api.picarto.tv/api/v1/channel/name/{}/videos".format(getChannel), headers=FileSystem().getHeader(), stream=True)
		if getRequest.status_code == 200: 
			for x in getRequest.json():
				# If the Information is Existed
				if x["id"] == int(getVideoID): 
					x1 = x
					x1["channel"] = getChannel
					x1.update()

					return {
						"isError": False,
						"ErrorSummary": "",
						"Information": x1
					}

		# Else if it is gone or non-Existed
		return {
			"isError": False,
			"ErrorSummary": "",
			"Information": {}
		}

	except Exception as e:
		return {
			"isError": True,
			"ErrorSummary": str(e)
		}

def getFilesize(url=""): 
	getInfo = requests.get(url, headers=FileSystem().getHeader(), stream=True) 

	return len(getInfo.content) if getInfo.status_code == 200 else 0

def getPlaylist(url=""):
	try:
		# Get index.m3u8 via URL in API
		getFile = requests.get(url, headers=FileSystem().getHeader(), stream=True)
		getSessionID = getFile.text.split("\n")[2] if getFile.status_code == 200 else ""
		# Get index.m3u8 with Video Fragment File Listed via URL in API
		getFile = requests.get(url.replace("index.m3u8", getSessionID), headers=FileSystem().getHeader(), stream=True)
		# getM3u8 = m3u8.loads(getFile.text if getFile.status_code == 200 else "")
		getM3u8 = m3u8.loads(getFile.text if getFile.status_code == 200 else "")
		getSize = 0

		setList = []		
		for x in getM3u8.segments:
			setList.append({
				"title": x.uri.split("?")[0],
				"sessId": x.uri.split("?")[1],
				"url": url.replace("index.m3u8", getSessionID.split("index.m3u8")[0]+ x.uri)
			})		

		return {
			"isError": False,
			"ErrorSummary": "",
			"sessId": getSessionID,
			"Rawm3u8": str(getM3u8),
			"Listm3u8": setList
		}

	except Exception as e:
		return {
			"isError": True,
			"ErrorSummary": str(e)
		}

def getCover(url=""): return requests.get(url, headers=FileSystem().getHeader(), stream=True).content

def getDownload(url="", title="", path=""):
	try:
		with requests.get(url, headers=FileSystem().getHeader(), stream=True) as r, open(path+ "/" +title, "wb") as f, tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=len(requests.get(url, headers=FileSystem().getHeader(), stream=True).content), file=sys.stdout, desc=title) as p:
			for x in r.iter_content(chunk_size=1024):
				ds = f.write(x)
				p.update(ds)

		return True

	except Exception as e:
		return False

#--------------------------------------------------------------------

# def constructVideo(files=[], name="", count=0):

# 	a = VideoFileMerger()
# 	for a1 in files: a.insertVideo(a1)

# 	a.run("{} - {}".format(name, str(count).zfill(5)), FileSystem().getPath)

# h1 = 0
# def getLevel(x1):
# 	global h1

# 	x2 = math.ceil(x1 / psutil.cpu_count(logical=True))

# 	if math.ceil(x1) == 1: pass
# 	else:
# 		h1 += 1 
# 		getLevel(x2)

# def run(output="", path=""):
# 	files = []
# 	fileCount = 0
# 	for x in os.listdir(path):
# 		if os.path.splitext(x)[1] == ".ts" or os.path.splitext(x)[1] == ".mkv":
# 			if len(open(FileSystem().getPath+ "/" + x, "rb+").read()) != 0:	files.append(FileSystem().getPath+ "/" +x)

# 	files.sort()

# 	x = math.ceil(len(files) / psutil.cpu_count(logical=True))
# 	prepareThread = []
# 	prepareCount = 0
# 	for x1 in range(x):
# 		tempFile = []

# 		for x2 in range(psutil.cpu_count(logical=True)):
# 			try:
# 				tempFile.append(files[fileCount])
# 				fileCount += 1
# 			except Exception as e: pass
			
# 		prepareThread.append(threading.Thread(target=constructVideo, args=(tempFile, output, prepareCount) ))
# 		prepareCount += 1
# 	# print(prepareThread)
# 	for x1 in prepareThread: x1.start()
# 	for x1 in prepareThread: x1.join()
# 	for x1 in files: os.remove(x1)


# files = []
# for x in os.listdir(FileSystem().getPath):
# 	if os.path.splitext(x)[1] == ".ts" or os.path.splitext(x)[1] == ".mkv":
# 		if len(open(FileSystem().getPath+ "/" + x, "rb+").read()) != 0:	files.append(FileSystem().getPath+ "/" +str(int(os.path.splitext(x)[0])).zfill(5) + os.path.splitext(x)[1])

# files.sort() # Sorting all the files but naming is kinda stucked out there
# getLevel(len(files))

# for x in range(h1):
# 	run("output "+ str(x).zfill(5), FileSystem().getPath)
# 	for x1 in range(5):
# 		print(x1)
# 		time.sleep(1)

