from core import CoreProcess

core_process = CoreProcess()

input_sentences = core_process.read_input_text_and_get_sentences('./datafiles/testinputs.txt')

df = core_process.set_matching_db_file('../../syrremk_new_add reason column.xls')

result = core_process.process_translation(df, input_sentences)

print(result)