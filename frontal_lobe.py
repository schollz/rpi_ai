import config
import os

# Get Google Tasks
def getTasks(dayBool):
	if not config.tasksLoaded:
		loadTasks()
		config.tasksLoaded = True
	if dayBool==0:
		myTasks = ""
		numTasks = 0
		with open("tasks_today.txt") as f:
			for line in f:
				a=line.split(".")
				b=a[1].split(":")
				c=b[0].strip()
				if numTasks == 0:		
					myTasks = c
				else:
					myTasks = myTasks + ". Also, you have to " + c
				numTasks = numTasks+1
		if numTasks==0:
			return "You do not have to do anything next today! Relax, man!"
		else:
			return "You have " + str(numTasks) + " things to do today. You have to " + str(myTasks)
	if dayBool==1:
		myTasks = ""
		numTasks = 0
		with open("tasks_nextweek.txt") as f:
			for line in f:
				a=line.split(".")
				b=a[1].split(":")
				c=b[0].strip()
				if numTasks == 0:		
					myTasks = c
				else:
					myTasks = myTasks + ". Also, you have to " + c
				numTasks = numTasks+1
		if numTasks==0:
			return "You do not have to do anything next week! Relax, man!"
		else:
			return "You have " + str(numTasks) + " things to do next week. You have to " + str(myTasks)

			
def loadTasks():
	os.system("python myTasks2.py -l 'Zack-todo' > current_tasks.txt")
	os.system("rm tasks_today.txt")
	os.system("touch tasks_today.txt")
	today = datetime.date.today()
	todayStr = today.strftime("%Y-%m-%d")
	os.system("cat current_tasks.txt | grep " + todayStr + " > tasks_today.txt")
	os.system("rm tasks_nextweek.txt")
	os.system("touch tasks_nextweek.txt")
	for x in range(1,7):
		today = datetime.date.today()+datetime.timedelta(days=x)
		todayStr = today.strftime("%Y-%m-%d")
		os.system("cat current_tasks.txt | grep " + todayStr + " >> tasks_nextweek.txt")
