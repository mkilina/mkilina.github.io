from morphology_check import *

def morphology_checker(text):
    mistakes = correction(text)
    print(mistakes)
    if isinstance(mistakes, list):
        mistakes_ids = [ { 'bos': line['start_id'], 'end': line['end_id'] } for line in mistakes ]
        print(mistakes_ids)
        return mistakes_ids
    else:
        print("Wrong datatype")
    # return [{'bos':5, 'end':15}, {'bos':20, 'end':300},]

def dummy_duplicates_checker(text):
    return [{'bos':12, 'end':25}]