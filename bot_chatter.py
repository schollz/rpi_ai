from chatterbotapi import ChatterBotFactory, ChatterBotType

def getAIresponse(s):
	try: 
		return getAIresponse2(s)
	except:
		return "Sorry, I can't do that."

def getAIresponse2(s):
	factory = ChatterBotFactory()
	bot2 = factory.create(ChatterBotType.CLEVERBOT)
	bot2session = bot2.create_session()
	response = bot2session.think(s)
	return response