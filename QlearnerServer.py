from mdp import *
from maploader import *
import random, pickle, copy, time

#Hyperparameters
totalEpisodes = 100
maxRolloutLength = 100
learningRate = 0.1
discountFactor = 0.95
epsilon = 0.85
epsilonDecay = 0.01
random.seed(1)

#breeding and killing parameters
breedChance = 0.3
killChance = 0.3
lastMapName = ""
lastMapAgent = ""
lastMapAgentStillAlive = False

actions = ["r", "l", "u", "d"]
agents = ["Sally", "Brandon", "Peach", "Dawn", "Don"]

def ChildNameGeneration(parent1, parent2):
	parent1NameContribution = parent1[:min(random.randint(0, len(parent1)),1)]
	parent2NameContribution = parent2[random.randint(0, len(parent2)-1):]
	return parent1NameContribution+parent2NameContribution

def ChildQTable(qTable1, qTable2):
	childQTable = {}
	for key in qTable1.keys():
		if key in qTable2.keys():
			childQTable[key] = random.choice([qTable1[key], qTable2[key]])
		else:
			childQTable[key] = qTable1[key]

	for key in qTable2.keys():
		if not key in qTable1.keys():
			childQTable[key] = qTable2[key]
	return childQTable

qTables = {}
for a in agents:
	if os.path.exists("./"+a+"qTable.pickle"):
		qTables[a] = pickle.load(open("./"+a+"qTable.pickle", "rb"))
	else:
		qTables[a] = {}

while True:
	time.sleep(3)
	print (" ")
	envs = GrabEnvironments()
	currEnv = random.choice(envs)
	
	currAgent = random.choice(agents)
	qTable = qTables[currAgent]

	print ("Dagochi "+currAgent+": playing "+str(currEnv.mapName)+"!")
	SARs = []
	rolloutComplete = False
	rolloutIndex = 0
	totalReward = 0

	while rolloutIndex < maxRolloutLength and not rolloutComplete:
		rolloutIndex+=1

		state = State(currEnv)

		#Action Selection
		action = random.choice(actions)
		if state.state in qTable.keys():
			maxAction = action
			maxValue = -1000

			for a in actions:
				if a in qTable[state.state].keys():
					if maxValue < qTable[state.state][a]:
						maxValue = qTable[state.state][a]
						maxAction = a
			action = maxAction
		else:
			action = random.choice(actions)


		if random.random()>epsilon:
			action = random.choice(actions)
		if epsilon<1:
			epsilon+=epsilonDecay


		#s_(t+1) <- s_t
		nextEnvironment = currEnv.child()

		if action=="r":
			nextEnvironment = MoveRight(nextEnvironment)
		elif action =="l":
			nextEnvironment = MoveLeft(nextEnvironment)
		elif action =="u":
			nextEnvironment = MoveUp(nextEnvironment)
		elif action =="d":
			nextEnvironment = MoveDown(nextEnvironment)

		reward = CalculateReward(currEnv, nextEnvironment)
		totalReward+=reward

		SARs.append([state.state, action, reward])
		currEnv = nextEnvironment

		#Check if complete
		if len(currEnv.playerPos)==0 or currEnv.totalCrystals==currEnv.collectedCrystals:
			rolloutComplete = True

	#print ("Episode: "+str(i)+" total reward: "+str(totalReward))

	# Q-update
	for j in range(len(SARs)-1, 0, -1):
		oldQValue = random.randrange(-100,100)#assume 0 initialization
		optimalFutureValue = oldQValue

		if SARs[j][0] in qTable.keys():
			if SARs[j][1] in qTable[SARs[j][0]].keys():
				oldQValue = qTable[SARs[j][0]][SARs[j][1]]

			if j+1<len(SARs)-1:
				for a in actions:
					if a in qTable[SARs[j+1][0]].keys():
						if optimalFutureValue < qTable[SARs[j+1][0]][a]:
							optimalFutureValue = qTable[SARs[j+1][0]][a]
			else:
				optimalFutureValue = oldQValue

		newQValue = oldQValue + learningRate*(SARs[j][2] + discountFactor*optimalFutureValue - oldQValue)

		if not SARs[j][0] in qTable.keys():
			qTable[SARs[j][0]] = {}
		qTable[SARs[j][0]][SARs[j][1]] = newQValue


	qTableSum = 0
	for keys in qTable.keys():
		for keys2 in qTable[keys].keys():
			qTableSum += qTable[keys][keys2]

	qTables[currAgent] = qTable

	#print ("Q table sum: "+ ("%0.2f" %qTableSum))
	print ("--- Dagochi "+currAgent+" managed to collect "+str(totalReward)+" reward! They reached "+str(rolloutIndex)+"%"+" of their step goals! ---")


	#Breeding and Killing Stuff

	if lastMapName==currEnv.mapName:
		if not lastMapAgent==currAgent:
			if random.random() <= breedChance:
				#Breed
				childName = ChildNameGeneration(currAgent,lastMapAgent)
				childQTable = ChildQTable(qTables[currAgent], qTables[lastMapAgent])
				agents.append(childName)
				qTables[childName] = childQTable
				print ("--- Congratulations to "+currAgent+" and "+lastMapAgent+" for the birth of their child "+childName+"! ---")

			if random.random() <= killChance:
				#Kill 
				agents.remove(lastMapAgent)
				print ("--- Oh no! "+currAgent+" just killed "+lastMapAgent+"! They will be missed. ---")



	#Mood Stuff

	mood = qTableSum
	depressed = False

	if mood < -500:
		depressed = True

	if not depressed:
		if totalReward<-100:
			print ("Dagochi "+currAgent+": ε(´סּ︵סּ`)з")
			print ("Dagochi "+currAgent+": Oh I didn't do very well, but I'll get better!")
		if totalReward<=0 and totalReward>=-100:
			print ("Dagochi "+currAgent+": ¯\\(°_o)/¯")
			print ("Dagochi "+currAgent+": Well, at least I'm not dead!")
		if totalReward>0:
			print ("Dagochi "+currAgent+": ᕕ( ᐛ )ᕗ")
			print ("Dagochi "+currAgent+": Oh wow I did great!")
	else:
		if totalReward<0: 
			print ("Dagochi "+currAgent+": (︶︹︶)")
			print ("Dagochi "+currAgent+": Of course it went badly.")
		if totalReward>=0:
			print ("Dagochi "+currAgent+": (ﾉ◕ヮ◕)ﾉ")
			print ("Dagochi "+currAgent+": Whoa! That was fun!")
		

	pickle.dump(qTable,open(currAgent+"qTable.pickle", "wb"))
	lastMapName = ""+currEnv.mapName
	lastMapAgent = ""+currAgent
	lastMapAgentStillAlive = len(currEnv.playerPos)>0



