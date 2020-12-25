import mysql.connector
import pandas as pd
import os
import tempfile
import re
import time
from parsing import *
from random import randint, uniform
from conllu import parse, parse_tree

from string import punctuation
punctuation += '«»—…“”–•'
punctuation = set(punctuation)
from nltk.corpus import stopwords
stops = stopwords.words('russian')

numbers = re.compile("[0-9]")
latins = re.compile(r"([a-zA-Z]+\W+)|(\W+[a-zA-Z]+)|(\W+[a-zA-Z]\W+)|([a-zA-Z]+)")
cyrillic = re.compile(r"([а-яА-ЯёЁ]+\W+)|(\W+[а-яА-ЯёЁ]+)|(\W+[а-яА-ЯёЁ]\W+)")
initial = re.compile(r"[а-яА-ЯёЁ]\.")

con = mysql.connector.connect(user='andrea',
                              password='rstq!2Ro',
                              host='127.0.0.1',
                              database='cat',
                              auth_plugin='mysql_native_password'
                             )

class Tagset:
    def __init__(self, unigram, lemm, morph, pos, start_id, end_id):
        self.unigram = unigram
        self.lemm = lemm
        self.morph = morph
        self.pos = pos
        self.start_id = start_id
        self.end_id = end_id

    def morph_to_string(self):
        if self.morph:
            subtaglist = list()
            for tag_element in list(self.morph.items()):
                subtag = '{}={}|'.format(tag_element[0], tag_element[1])
                subtaglist.append(subtag)

            fulltag = ''.join([str(x) for x in subtaglist])
            morph_string = fulltag[:-1]
            return morph_string
        else:
            morph_string = 'None'
            return morph_string
    
    def to_dict(self):
        return dict([('unigram', self.unigram), ('lemm', self.lemm), ('morph', self.morph), \
            ('pos', self.pos), ('start_id', self.start_id), ('end_id', self.end_id)])

# TODO: combine funcitons "add_ids" and "get_words" 

def add_ids(conllu_sents, text, prev_text_len=0):
    text_copy = text
    print(conllu_sents)
    for sent in conllu_sents:
        for token in sent.tokens:
            form = token['form']
            position = text_copy.find(form)
            token['start_id'] = prev_text_len + position
            token['end_id'] = prev_text_len + position + len(form)
            text_copy = text[position+len(form):]
            prev_text_len = prev_text_len+position+len(form)
    for token in conllu_sents:
        yield token
    # return conllu_sents

def parser(conllu, from_file=False):
    """
    Yields a sentence from conllu tree with its tags

    """
    if from_file:
        with open(conllu, 'r', encoding='utf-8') as f:
            conllu = f.read()

    tree = parse(conllu)

    for token in tree:
        yield token


def get_words(conllu):
    """
    tree - generator of sentences (TokenLists) from conllu tree
    txtfile - txt version of the conllu file

    words, list is a list of all tokens we need from the tree
    size, int is a number of all words in the domain
    """

    words = []

    conllu_sents = parse(conllu)

    for sentence in conllu_sents:
        for token in sentence:
            token_range = token['misc']['TokenRange']
            start, end = token_range.split(':')
            token['start_id'], token['end_id'] = int(start), int(end)

            if token['form'] != '_' and token['upostag'] != '_' and token['upostag']!='NONLEX' and token['form'] not in r'[]\/':
                for unigram in token['form'].split(): # .lower()
                    words.append((unigram, token['lemma'], token['feats'], token['upostag'],
                    token['start_id'], token['end_id']))

    size = len(words)
    return words, size

def tagset_lemma(words):
    """
    Expands OrderedDict object to string
    words: list of tuples (unigram, lemm, morph, pos, start_id, end_id)
    """
    print('tagset being created...')
    word_list = list()
    for word in words:
        tagset = Tagset(*word)
        tagset.morph = tagset.morph_to_string()
        tagset = tagset.to_dict()
        word_list.append(tagset)
    return word_list


def morph_error_catcher(words):
    mistakes = {}
    corrects = {}
    cur = con.cursor(dictionary=True, buffered=True)
    for i, word in enumerate(words):
        if word['unigram'].lower() not in punctuation and word['unigram'].lower() not in stops and \
        not numbers.match(word['unigram'].lower()) and not latins.search(word['unigram'].lower()) and \
        not cyrillic.search(word['unigram'].lower()) and word['pos'] != 'PROPN':

            time.sleep(uniform(0.2, 0.6))

            cur.execute("""SELECT unigram, lemm, morph, pos FROM
                        (SELECT unigram, morph, lemma FROM unigrams) AS a JOIN
                        (SELECT id_lemmas, id_pos, lemma AS lemm FROM lemmas) AS b ON lemma = id_lemmas JOIN pos ON b.id_pos = pos.id_pos
                        WHERE unigram="{}" &&
                        lemm="{}" &&
                        morph="{}" &&
                        pos="{}";""".format(word['unigram'], word['lemm'], word['morph'], word['pos']))

            rows = cur.fetchall()
            if not rows:
                mistakes[i] = word
            else:
                corrects[i] = word
    return mistakes, corrects


def correction(text, corrected_files_directory='corrections', print_correction=False, from_file=False):
    '''
    conllu: path to conllu format file or conllu data
    text: variable open in 'r' mode
    corrected_files_directory: directory path where the corrected txt file should end up
    print_correction = flag in to get a txt file with correction in the destination directory
    '''

    conllu = make_conll_with_udpipe(text)
    # tagset creation
    words, _ = get_words(conllu)
    # del tree   
    
    
    tagset = tagset_lemma(words)
    mistakes, _ = morph_error_catcher(tagset)
    mistakes_list = mistakes.values()

    if print_correction == True:

        tot=0
        mists=0
        correction = list()
        for i, word in enumerate(tagset):
            if i in mistakes:
                correction.append('++'+word['unigram']+'++')
                mists+=1
                tot+=1
            else:
                correction.append(word['unigram'])
                tot+=1
        correction = ' '.join(correction)

        os.makedirs(os.path.join(os.getcwd(), corrected_files_directory), exist_ok=True)
        with open(os.path.join(corrected_files_directory, filename[:-6]+'txt'), 'w', encoding='utf-8') as fw:
            fw.write(correction)
            fw.write('\n\n')
            fw.write(str(mistakes_list))
        print(correction, "\n\nCorrected words: %s" %mists, "\nMistake frequency: %s" %(mists/tot))

    return list(mistakes_list)

STUD_DIR = r'C:\Users\Andrea\Desktop\The_Cartella_2.0\uni\second_year\cat\stud_textVSscie_text\Student_texts_for_experiments\stud_txt'
LOW_LVL = os.path.join(STUD_DIR, 'Low Level')
REG_LVL = os.path.join(STUD_DIR, 'Regular Level')
LOW_PRSD = os.path.join(STUD_DIR, 'conllu', 'Low_Level_Parsed')
REG_PRSD = os.path.join(STUD_DIR, 'conllu', 'Regular_Level_Parsed')
MA_THESES=r'C:\Users\Andrea\Desktop\stud_textVSscie_text\Student_texts_for_experiments\Fin_MA_theses_parsed'
CORR_DIR = r'C:\Users\Andrea\Desktop\corrected_files'

test_txt = os.path.join(REG_LVL, 'EC12-B1-0732.txt')
test_conllu = os.path.join(REG_PRSD, 'prs_EC12-B1-0732.conllu') 
test_txt = os.path.join(os.getcwd(), 'student_texts', 'f200bce2444711eba31d543530ccc142.txt')

def main():
    
    print('none')

if __name__ == "__main__":
    main()