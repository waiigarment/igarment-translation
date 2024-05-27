import spacy
import re
# need to load these modules for defining and registering translation component
from translation_component import TranslationComponent, create_translation_component
from garment_lemmatizer import GarmentLemmatizer, create_garment_lemmatizer

import pandas as pd
import numpy as np
from openpyxl import load_workbook
import xlrd
import xlwt
from pandas.io.excel import ExcelWriter
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from datetime import datetime
from pyexcelerate import Workbook
import os
from utils import *
from spacy.language import Language

@Language.component("custom_boundaries")
def set_custom_boundaries(doc):
    for token in doc[:-1]:
        if token.text == '\n' and doc[token.i + 1].text in '、。？，,':
            token.is_sent_start = False
            doc[token.i + 1].is_sent_start = True
    return doc

# Custom sentencizer
def sentencize(text):
    # Define the pattern to find '\n' preceded by specified characters
    pattern = r'([、。？，,])\n'
    # Replace the pattern with the character itself (captured group 1) followed by ''
    result = re.sub(pattern, r'\1', text)
    
    return result

def load_updated_model(model_dir='igarment_translation_model_v1'):
    nlp = spacy.load(model_dir)
    return nlp

def create_updated_new_translation(translation_db_file_path: str, data, output_dir = 'updated_outputs'):
    if not translation_db_file_path.endswith(('.xls', '.xlsx')):
        raise ValueError("The file path must end with '.xls' or '.xlsx'")
        
    translation_db_file_path_xlsx = translation_db_file_path
    
    xlsx = pd.ExcelFile(translation_db_file_path_xlsx)
    sheet_names = xlsx.sheet_names
    
    df = pd.read_excel(translation_db_file_path_xlsx)
    
    new_row_df = pd.DataFrame(data)

    df = pd.concat([df, new_row_df], ignore_index=True)
    
    final_output_file_path = add_new_sub_dir_file_path(translation_db_file_path_xlsx, output_dir)
    final_output_file_path = add_suffix_to_filename(final_output_file_path, datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    
    with pd.ExcelWriter(final_output_file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_names[0])

        worksheet = writer.sheets[sheet_names[0]]
        
        column_widths = {
            'jp': 30,
            'vn (original)': 30,
            'vn (updated)': 40,
            'Reason': 40,
            'en': 40,
            'zh-tc': 40
        }

        format_worksheet(df, worksheet, column_widths)

    return final_output_file_path
        
def user_verify_translation(origianl, translation, translated_with_chatgpt_flag, combined_sentence, combined_translated_text):
    print(f"Origianl: {origianl}")
    
    corrected_translation = translation
    if translated_with_chatgpt_flag:
        print(f"Translation[from chatgpt]: {translation}")
        correct = input("Is the translation correct? (y/n) ('Enter' = 'y'): ")
        if correct.lower() == 'n':
            corrected_translation = input("Please provide the correct translation: ")
            print('Will update the corrected translation to translation database.')
        else:
            print('Will update the new translation to translation database.')
    else:
        if combined_translated_text:
            corrected_translation = combined_translated_text
            print(f"Found sentence [with combination]: {combined_sentence}")
            print(f"Translation[from database]: {combined_translated_text}")
        else:
            print(f"Translation[from database]: {translation}")
            
    print()        
    return origianl, corrected_translation

def translate_with_custom_component(nlp, sentence):
    doc = nlp(sentence)
    
    translations_to_update = []
    
    print('########## Transaltion Results will be shown below. ##########', end='\n\n')
    
    for sent in doc.sents:
        origianl, corrected_translation = user_verify_translation(
            sent.text.strip(), 
            sent._.translated_text, 
            sent._.translated_with_chatgpt,
            sent._.combined_sentence,
            sent._.combined_translated_text
            )
        
        if sent._.translated_with_chatgpt:
            translations_to_update.append({
                'jp': origianl,
                'vn (original)': corrected_translation,
                'vn (updated)': np.nan,
                'Reason': np.nan,
                'en': np.nan,
                'zh-tc': np.nan
            })
    
    if len(translations_to_update) > 0:
        print('There are updated translations to add newly.')
        translation_db_file_path = input("Enter the path of translation file that you want to update (Enter for default path './translation_db_files/original_trans_db_1.xls'): ")
        if translation_db_file_path == '':
            translation_db_file_path = './translation_db_files/original_trans_db_1.xls'
        updated_file_path = create_updated_new_translation(translation_db_file_path, translations_to_update, 'updated_outputs')
        print('The updated translation file path is ', updated_file_path)
    return True

##### Testing the model ####
model_dir_name = input("Enter the model_dir_name to use (Enter for default name 'igarment_translation_model_v1'): ")
if model_dir_name == '':
    model_dir_name = "igarment_translation_model_v1"
    
nlp2 = load_updated_model(model_dir_name)

input_text_file_path = input("Enter the path of input text file (Enter for default path './test_text_files/testinputs2.txt'): ")
print()
if input_text_file_path == '':
    input_text_file_path = './test_text_files/testinputs2.txt'
    
text = sentencize(extract_text_from_txt(input_text_file_path))
translated_sentence = translate_with_custom_component(nlp2, text)

