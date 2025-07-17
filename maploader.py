import os, glob, copy
from mdp import *

def ValidToken(strVal):
	return "C" in strVal or "F" in strVal or "A" in strVal or "-" in strVal

def GrabEnvironments():
	envs = []
	for filename in glob.glob("./maps/*.txt"):
		if os.path.exists(filename):
			source = open(filename, "r")
			mapText = []
			playerStartFound = False
			splits = filename.split("/")
			mapName = splits[-1][:-4]

			for line in source:
				mapLine = []
				line = line.rstrip()
				for i in range(0, len(line)):
					if (ValidToken(line[i])):
						mapLine.append(line[i])
						if line[i] == "A":
							playerStartFound = True
					else: 
						mapLine.append("-")
				mapText.append(mapLine)
			if not playerStartFound:
				mapText[0][0] = "A"
			envs.append(Environment(mapText, mapName))
	return envs
