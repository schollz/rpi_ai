def saySomething(txt,language):
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
                os.system("mpg123 -a hw:1 -q 'http://translate.google.com/translate_tts?tl="+language+"&q=" + sentence + "'")

