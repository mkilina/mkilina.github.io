from checking import dummy_morphology_checker, dummy_duplicates_checker

UPLOAD_FOLDER = 'student_texts'
ALLOWED_EXTENSIONS = {'txt'}
ASPECTS =  [{'id': 'morphology','russian': 'Словоформы, не представленные в CAT'},
           {'id': 'duplicates','russian': 'Повторы'}]
ASPECT2FUNCTION  = {
    'morphology': dummy_morphology_checker,
    'duplicates': dummy_duplicates_checker
}
