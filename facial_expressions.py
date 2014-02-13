from mouth_function import saySomething
import pygame, sys, time, random
from pygame.locals import *
from time import *
import curses
from curses.ascii import isdigit
import nltk
from nltk.corpus import cmudict
import os
import thread
import threading

d = cmudict.dict() 
		
def nsyl(word):
    return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]

def generateExpression(phrase):
	pygame.init()
	windowSurface = pygame.display.set_mode((500, 400), 0, 32)
	pygame.display.set_caption("Bounce")

	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	YELLOW = (255,255,0)

	info = pygame.display.Info()
	sw = info.current_w
	sh = info.current_h
	y = 0
	windowSurface.fill(WHITE)
	pygame.draw.circle(windowSurface, YELLOW , (250,200), 80, 0)
	pygame.draw.circle(windowSurface, BLACK,(280,170), 10, 0)
	pygame.draw.circle(windowSurface, BLACK,(220,170), 10, 0)

	pygame.draw.ellipse(windowSurface,BLACK,(225,230,50,10),0)
	myfont = pygame.font.SysFont("ComicSans", 35)
	pygame.display.update()
	sleep(1)
	paragraph =  str(sys.argv[1])
	thread.start_new_thread( saySomething,(paragraph,"en",))
	workingSentence = ""
	sleep(0.26)
	for phrase in paragraph.split("?"):
		for sentence in phrase.split("."):
			for word in sentence.split():
				windowSurface.fill(WHITE)
				pygame.draw.circle(windowSurface, YELLOW , (250,200), 80, 0)
				pygame.draw.circle(windowSurface, BLACK,(280,170), 10, 0)
				pygame.draw.circle(windowSurface, BLACK,(220,170), 10, 0)

				pygame.draw.ellipse(windowSurface,BLACK,(225,220,50,30),0)
				myfont = pygame.font.SysFont("ComicSans", 17)
				workingSentence += word + " "
				label = myfont.render(workingSentence, 1, BLACK)
				windowSurface.blit(label, (5, 5))
				pygame.display.update()
				syl = nsyl(word)
				syl = syl[0]
				sleep(0.185*float(syl))

				windowSurface.fill(WHITE)
				pygame.draw.circle(windowSurface, YELLOW , (250,200), 80, 0)
				pygame.draw.circle(windowSurface, BLACK,(280,170), 10, 0)
				pygame.draw.circle(windowSurface, BLACK,(220,170), 10, 0)

				pygame.draw.ellipse(windowSurface,BLACK,(225,230,50,10),0)
				myfont = pygame.font.SysFont("ComicSans", 17)
				label = myfont.render(workingSentence, 1, BLACK)
				windowSurface.blit(label, (5, 5))
				pygame.display.update()
				sleep(0.082)
			windowSurface.fill(WHITE)
			pygame.draw.circle(windowSurface, YELLOW , (250,200), 80, 0)
			pygame.draw.circle(windowSurface, BLACK,(280,170), 10, 0)
			pygame.draw.circle(windowSurface, BLACK,(220,170), 10, 0)

			pygame.draw.ellipse(windowSurface,BLACK,(225,230,50,10),0)
			myfont = pygame.font.SysFont("ComicSans", 17)
			label = myfont.render(workingSentence, 1, BLACK)
			windowSurface.blit(label, (5, 5))
			pygame.display.update()
			sleep(0.16)

	sleep(1)


