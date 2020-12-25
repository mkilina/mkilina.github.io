import codecs, re
from nltk import sent_tokenize
import pandas as pd
from collections import Counter

vowels = ["а", "я", "о", "ё", "у", "ю", "е", "э", "ы", "и", "á", "ó"]

# Readability

def countASLandASW(text):
    text = re.split("\n", text)
    text = [line.rstrip() for line in text]
    joinedText = re.sub('́', "", " ".join(text))
    joinedText = re.sub(" -+ ", " ", " ".join(text))
    words = re.findall('[\dáóа-яё-]+', joinedText.lower())
    words = [word for word in words if word != "-"]
    word_num = len(words)
    
    syll_num = 0
    for word in words:
        for letter in set(word):
            if letter in vowels: 
                syll_num += 1
    
    sentences = sent_tokenize(joinedText, 'russian')
    sent_num = len(sentences)
    
    ASL = word_num/sent_num #average sent length
    ASW = syll_num/word_num #average num of syllables per word
    return (ASL, ASW)

def countFRE(text):
    ASL, ASW = countASLandASW(text)
    FRE = 208.7 - 2.6 * ASL - 39.2 * ASW
    return(round(FRE, 2))

def uniqueWords(text):
    text = re.split("\n", text)
    text = [line.rstrip() for line in text]
    joinedText = re.sub('́', "", " ".join(text))
    joinedText = re.sub(" -+ ", " ", " ".join(text))
    words = re.findall('[\dáóа-яё-]+', joinedText.lower())
    words = [word for word in words if word != "-"]
    word_num = len(words)
    unique_word = len(set(words))
    return word_num, unique_word
