import codecs, re
from nltk import sent_tokenize
import pandas as pd
from collections import Counter

vowels = ["а", "я", "о", "ё", "у", "ю", "е", "э", "ы", "и", "á", "ó"]

# Readability

def countASLandASW(text):
    text = codecs.open(text, "r", "utf_8_sig").readlines()
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
    return(FRE)

# Frequent words rate

def ipm_CAT(df):
    df.f1 = df.f1.apply(lambda x: float((x*1000)/2494422))
    df.f2 = df.f2.apply(lambda x: float((x*1000)/2636290))
    df.f3 = df.f3.apply(lambda x: float((x*1000)/2691363))
    df.f4 = df.f4.apply(lambda x: float((x*1000)/1880004))
    df.f5 = df.f5.apply(lambda x: float((x*1000)/2808313))
    df.f6 = df.f6.apply(lambda x: float((x*1000)/1500196))
    return df

def getFreqTable(unigramsFreq):
    lemmas = pd.DataFrame(unigramsFreq, columns = ['lemma', 'POS', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6'])
    lemmas = ipm_CAT(lemmas)
    return lemmas
