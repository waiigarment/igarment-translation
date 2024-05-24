import spacy
import pandas as pd
# need to load these modules for defining and registering translation component
from translation_component import TranslationComponent, create_translation_component
from garment_lemmatizer import GarmentLemmatizer, create_garment_lemmatizer

def load_excel_file(file_path):
    df = pd.read_excel(file_path, engine='xlrd')
    return df

def train_custom_component(nlp, data):
    translation_component = nlp.get_pipe("translation_component")
    for index, row in data.iterrows():
        original = row['jp']
        # print('original', original)
        translated =  row['vn (updated)'] if pd.notna(row['vn (updated)']) else row['vn (original)']
        translation_component.add_translation(original, translated)
    return nlp

# Load core translation data of igarment
translation_db_file_path = input("Enter the path of translation_db_file to train (Enter for default path './translation_db_files/original_trans_db_1.xls'): ")
if translation_db_file_path == '':
    translation_db_file_path = './translation_db_files/original_trans_db_1.xls'
    
igarment_core_translation_data = load_excel_file(translation_db_file_path)
# print(igarment_core_translation_data)
garment_data = igarment_core_translation_data[igarment_core_translation_data['Reason'].str.contains('Garment terminology', case=False, na=False)]

garment_terms = []
for _, row in garment_data.iterrows():
    text = row['jp']
    garment_terms.append(text)

# can modify for customer speicific types
worker_names = ['田中', '山田', '鈴木', '佐藤', '伊藤']

nlp = spacy.blank("ja")

punct_chars = [
 '!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹', '।', '॥', '၊', '။', '።',
 '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄', '᥅', '᪨', '᪩', '᪪', '᪫',
 '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿', '‼', '‽', '⁇', '⁈', '⁉',
 '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶', '꡷', '꣎', '꣏', '꤯', '꧈',
 '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒', '﹖', '﹗', '！', '．', '？',
 '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀', '𑃁', '𑅁', '𑅂', '𑅃', '𑇅',
 '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼', '𑊩', '𑑋', '𑑌', '𑗂',
 '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐', '𑗑', '𑗒', '𑗓',
 '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂', '𑩃', '𑪛',
 '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈', '｡', '。', 
 # the following puncts are customs.
 '\n',
 ]

nlp.add_pipe("sentencizer", config={'punct_chars': punct_chars}, first=True)

# Add the custom translation component to the pipeline
nlp.add_pipe("translation_component", last=True)

# Add the custom lemmatizer to the pipeline with garment terms
nlp.add_pipe("garment_lemmatizer", config={"garment_terms": garment_terms})

# Add EntityRuler for custom garment terms and worker names
ruler = nlp.add_pipe("entity_ruler", after="garment_lemmatizer")
garment_patterns = [{"label": "GARMENT_TERM", "pattern": term} for term in garment_terms]
worker_patterns = [{"label": "WORKER_NAME", "pattern": name} for name in worker_names]
ruler.add_patterns(garment_patterns + worker_patterns)

# Train the custom component with translation database
nlp = train_custom_component(nlp, igarment_core_translation_data)

#### Saving the trained model

model_output_dir = input("Enter the model_output_dir_name (Enter for default name 'igarment_translation_model_v1'): ")

if model_output_dir == '':
    model_output_dir = "igarment_translation_model_v1"
    
nlp.to_disk(model_output_dir)

print(f"Model saved to {model_output_dir}")
