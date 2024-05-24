import spacy
import re
# need to load these modules for defining and registering translation component
from translation_component import TranslationComponent, create_translation_component
from garment_lemmatizer import GarmentLemmatizer, create_garment_lemmatizer

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

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text.replace("※", "")

def user_verify_translation(origianl, translation, translated_with_chatgpt_flag):
    print(f"Origianl: {origianl}")
    if translated_with_chatgpt_flag:
        print(f"Translation[from chatgpt]: {translation}")
    else:
        print(f"Translation[from database]: {translation}")
    print()
    
    if translated_with_chatgpt_flag:
        correct = input("Is the translation correct? (y/n) ('Enter' = 'y'): ")
        if correct.lower() == 'n':
            corrected_translation = input("Please provide the correct translation: ")
            print('Will update the corrected translation to translation database.')
        else:
            print('Will update the new translation to translation database.')

def translate_with_custom_component(nlp, sentence):
    doc = nlp(sentence)
    for sent in doc.sents:
        user_verify_translation(sent.text.strip(), sent._.translated_text, sent._.translated_with_chatgpt)
        # print(f"Original: '{sent.text.strip()}'")
        # print(f"Translated: '{sent._.translated_text}'")  
        # print()
    # return "\n".join([sent._.translated_text for sent in doc.sents])


##### Testing the model ####

model_dir_name = input("Enter the model_dir_name to use (Enter for default name 'igarment_translation_model_v1'): ")
if model_dir_name == '':
    model_dir_name = "igarment_translation_model_v1"
    
nlp2 = load_updated_model(model_dir_name)

input_text_file_path = input("Enter the path of input text file (Enter for default path './test_text_files/testinputs1.txt'): ")
if input_text_file_path == '':
    input_text_file_path = './test_text_files/testinputs1.txt'
    
text = sentencize(extract_text_from_txt(input_text_file_path))

translated_sentence = translate_with_custom_component(nlp2, text)

