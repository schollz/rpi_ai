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
import re

d = cmudict.dict() 

def saySomething(txt,language):
	#use alsamixer to check which is which (is 0 recording? or is 1?)
	#os.system("espeak -ven+f3 -k5 -s150 '" + txt + "'")
	print "speaking " + language
	words = txt.split()
	numWords = len(words)
	sentences = ""
	curSentence = 0
	curCharacters = 0
	curWord = 0
	for word in words:
		if curCharacters+len(word)+1<100:
			sentences = sentences+'%20'+word
		else:
			curSentence = curSentence + 1
			sentences = sentences + "111" + word
			curCharacters = 0
		curCharacters = curCharacters + len(word)+1
		curWord = curWord + 1
	
	feedTxt = sentences.split("111")
	for sentence in feedTxt:
		sentence = sentence.replace("'","%27")
		print sentence
		os.system('mpg123 -q "http://translate.google.com/translate_tts?tl='+language+'&q=' + sentence + '"')
		
def nsyl(word):
    return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
	
pygame.init()
windowSurface = pygame.display.set_mode((259, 271), 0, 32)
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
myfont = pygame.font.SysFont("ComicSans", 35)
img=pygame.image.load('animate/face_normal.png')
windowSurface.blit(img,(0,0))
pygame.display.update()
sleep(0.2)
paragraph =  str(sys.argv[1])
paragraph = re.sub('[!,;?]', '.', paragraph)
lastImage = img
for sentence in paragraph.split("."):
	try:
		thread.start_new_thread( saySomething,(sentence,"en",))
	except:
		pass
	workingSentence = " "
	sleep(0.24)
	for word in sentence.split():
		ipa = d[word.lower()]
		ipa = ipa[0]
		syl = nsyl(word)
		syl = syl[0]
		timePerChar = 0.244/float(len(ipa))
		for char in ipa:
			windowSurface.fill(WHITE)
			if "m" in char.lower() or "b" in char.lower() or "p" in char.lower():
				img=pygame.image.load('animate/face_mbp.png')
			elif "th" in char.lower():
				img=pygame.image.load('animate/face_th.png')
			elif "ee" in char.lower():
				img=pygame.image.load('animate/face_ee.png')
			elif "oo" in char.lower():
				img=pygame.image.load('animate/face_oo.png')
			elif "l" in char.lower():
				img=pygame.image.load('animate/face_l.png')
			elif "f" in char.lower() or "v" in char.lower():
				img=pygame.image.load('animate/face_fv.png')
			elif "g" in char.lower() or "sh" in char.lower() or "ch" in char.lower():
				img=pygame.image.load('animate/face_gshch.png')
			elif "s" in char.lower() or "d" in char.lower() or "t" in char.lower() or "r" in char.lower() or "k" in char.lower() or "c" in char.lower():
				img=pygame.image.load('animate/face_sdtrck.png')
			elif "a" in char.lower():
				img=pygame.image.load('animate/face_a.png')
			elif "o" in char.lower():
				img=pygame.image.load('animate/face_o.png')
			else:
				img = lastImage
			windowSurface.blit(img,(0,0))
			pygame.display.update()
			myfont = pygame.font.SysFont("ComicSans", 17)
			workingSentence += char[0]
			label = myfont.render(workingSentence, 1, BLACK)
			windowSurface.blit(label, (5, 5))
			pygame.display.update()
			sleep(timePerChar)
			lastImage = img
		workingSentence += " "
		windowSurface.fill(WHITE)
		img=pygame.image.load('animate/face_normal.png')
		lastImage = img
		windowSurface.blit(img,(0,0))
		pygame.display.update()
		myfont = pygame.font.SysFont("ComicSans", 17)
		label = myfont.render(workingSentence, 1, BLACK)
		windowSurface.blit(label, (5, 5))
		pygame.display.update()
		sleep(0.04)
	windowSurface.fill(WHITE)

	myfont = pygame.font.SysFont("ComicSans", 17)
	label = myfont.render(workingSentence, 1, BLACK)
	img=lastImage
	windowSurface.blit(img,(0,0))
	windowSurface.blit(label, (5, 5))
	pygame.display.update()
	sleep(0.4)

sleep(1)


