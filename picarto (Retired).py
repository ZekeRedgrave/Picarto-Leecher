import tqdm, ffmpeg
import requests, os, threading

path = os.path.dirname(os.path.realpath(__file__))

def getTS(currVideo):
	global path

	arr = []
	thread = []
	count = 0

	_currVideo = currVideo.replace(".mkv", ".m3u8")	
	readFile = open(path+ "\\temp\\" +_currVideo, "r+")

	splitA = readFile.read().split(",")[4].rstrip()
	splitB = splitA.split('"')[1].replace("\n", "")
	splitC = splitB.split("/")[0]

	readFile = open(path+ "\\temp\\list_" +_currVideo, "r+").read()

	for a in readFile.split("#"): 
		if len(a.split(",")) == 2: arr.append(a.split(",")[1].rstrip().replace("\n", ""))

	print("File Completion: 0 to "+ str(len(arr) - 1))

	# Download All Video Stream Fragment (19 Workers per Batch)
	batchCount = 1
	tempArr = []

	for a in range(0, len(arr)):
		x = threading.Thread(target=downloadTS, args=(currVideo, splitC+ "/"+ arr[a]))
		tempArr.append(x)

		if a == 19 * batchCount:
			print(tempArr)
			print("batch #"+ str(batchCount))
			batchDownload(tempArr)

			tempArr.clear()
			batchCount += 1

			os.system("cls")

		if a == len(arr) - 1:
			print("batch #"+ str(batchCount))
			batchDownload(tempArr)

			tempArr.clear()

	# Create Text File
	string = ''''''

	for a in readFile.split("#"): 
		if len(a.split(",")) == 2: 
			splitA = a.split(",")[1].rstrip().replace("\n", "")
			splitB = splitA.split("?")[0]

			if os.path.isfile(path+ "\\download\\" + splitB) is True:
				string += '''file ''' +path.replace("\\", "/")+ "/download/" + splitB+ '''\n'''


	open(path+ "\\"+ currVideo.replace(".mkv", ".txt"), "w+").write(string)

def batchDownload(x):
	workArr = []

	for a in x:
		print(a)

		workArr.append(a)
		a.start()

	for b in workArr: b.join()

def getIndex(currVideo):
	global path

	_currVideo = currVideo.replace(".mkv", ".m3u8")

	r = requests.get('https://recording-eu-1.picarto.tv/playhls/' +str(currVideo)+ '/index.m3u8', stream=True)
	with open(path+ "\\temp\\" +_currVideo, "wb+") as writeFile:
		for x in tqdm.tqdm(iterable=r.iter_content(chunk_size=1024), total=int(r.headers["content-length"]) / 1024, unit="KB"):
			writeFile.write(x)

	with open(path+ "\\temp\\" +_currVideo, "r+") as readFile:
		splitA = readFile.read().split(",")[4].rstrip()
		splitB = splitA.split('"')[1].replace("\n", "")

		r = requests.get(' https://recording-eu-1.picarto.tv/playhls/' +str(currVideo)+ '/'+ splitB, stream=True)
		with open(path+ "\\temp\\list_" +_currVideo, "wb+") as writeFile:
			for x in tqdm.tqdm(iterable=r.iter_content(chunk_size=1024), total=int(r.headers["content-length"]) / 1024, unit="KB"):
				writeFile.write(x)

def downloadTS(currVideo, ts):
	global path

	try:
		splitA = ts.split("/")[1]
		splitB = splitA.split("?")[0]

		r = requests.get(' https://recording-eu-1.picarto.tv/playhls/' +str(currVideo)+ '/' +ts, stream=True)

		with open(path+ "\\download\\" +splitB, "wb+") as writeFile:
			for x in tqdm.tqdm(iterable=r.iter_content(chunk_size=1024), unit="KB"):
				writeFile.write(x)
	except Exception as e:
		downloadTS(currVideo, ts)

def mergeTS(currVideo):
	global path

	ffmpeg.input(path+ "\\"+ currVideo.replace(".mkv", ".txt"), f="concat", safe=0).output(path+ "\\"+ currVideo.replace(".mkv", ".avi"), c="copy").run()

def main():
	global path

	# try:
	# 	print("Picarto Leecher Version 0")
	# 	print("Developer: Redgrave <<-- Asshole")

	# 	print("\n\n[Type 'url' to Download the Video Fragment]")
	# 	print("[Type 'merge' to puzzle all Videos Fragment into Single File]")

	# 	option = input("\n$ > ")

	# 	if option.lower() == 'url':
	# 		getUrl = input("$ Url > ").split("/")

	# 		if getUrl[2].lower() == "picarto.tv": 
	# 			os.system('cls')
	# 			getIndex(getUrl[4])

	# 			os.system('cls')
	# 			getTS(getUrl[4])
				
	# 			os.system('cls')
	# 			print("$ > Video Fragment name '"+ getUrl[4] +"' Downloaded Complete!\n")
	# 			main()

	# 	if option.lower() == 'merge':
	# 		file = input("$ Video Fragment(Ex blob.mkv) > ")

	# 		if os.path.isfile(path+ "\\" +file.replace(".mkv", ".txt")) is True:
	# 			getFile = open(path+ "\\" +file.replace(".mkv", ".txt"), "r+").read().replace("\n", "").split("file ")
	# 			notCount = 0
	# 			notArray = []

	# 			for x in getFile:
	# 				if os.path.isfile(x) is False:
	# 					notArray.append(x)
	# 					notCount += 1

	# 			if notCount == 0:
	# 				os.system('cls')
	# 				print("Error > Missing file is Detected!\n")
	# 				print("Error > "+ str(notCount) + " is Missing!")
	# 				print(notArray)
	# 				print()
	# 				main()

	# 			else:
	# 				os.system('cls')
	# 				mergeTS(file)

	# 				os.system('cls')
	# 				main()

	# 		else:
	# 			os.system('cls')
	# 			print("Error > Not Found!\n")
	# 			main()

	# 	else:
	# 		os.system('cls')
	# 		print("Error > Please Try Again!\n")
	# 		main()

	# except Exception as e:
	# 	print("Error > " +str(e)+ "\n")
	# 	main()

	print("Picarto Leecher Version 0")
	print("Developer: Redgrave <<-- Asshole")

	print("\n\n[Type 'url' to Download the Video Fragment]")
	print("[Type 'merge' to puzzle all Videos Fragment into Single File]")

	option = input("\n$ > ")

	if option.lower() == 'url':
		getUrl = input("$ Url > ").split("/")

		if getUrl[2].lower() == "picarto.tv": 
			os.system('cls')
			getIndex(getUrl[4])

			os.system('cls')
			getTS(getUrl[4])
				
			os.system('cls')
			print("$ > Video Fragment name '"+ getUrl[4] +"' Downloaded Complete!\n")
			main()

	if option.lower() == 'merge':
		file = input("$ Video Fragment(Ex blob.mkv) > ")

		if os.path.isfile(path+ "\\" +file.replace(".mkv", ".txt")) is True:
			getFile = open(path+ "\\" +file.replace(".mkv", ".txt"), "r+").read().replace("\n", "").split("file ")
			notCount = 0
			notArray = []

			for x in getFile:
				if os.path.isfile(x) is False:
					notArray.append(x)
					notCount += 1

			if notCount == 0:
				os.system('cls')
				print("Error > Missing file is Detected!\n")
				print("Error > "+ str(notCount) + " is Missing!")
				print(notArray)
				print()
				main()

			else:
				os.system('cls')
				mergeTS(file)

				os.system('cls')
				main()

		else:
			os.system('cls')
			print("Error > Not Found!\n")
			main()

	else:
		os.system('cls')
		print("Error > Please Try Again!\n")
		main()

if __name__ == "__main__":
	if os.path.isdir(path+ "\\temp") is False: os.makedirs(path+ "\\temp")
	if os.path.isdir(path+ "\\download") is False: os.makedirs(path+ "\\download")

	main()