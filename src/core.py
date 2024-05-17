import pandas as pd
import spacy
from openai import OpenAI
import os
from utils.commons import is_file_descriptor, is_file_path

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

languages = {
    'en': 'English',
    'jp': 'Japanese',
    'vm': 'Vietnamese',
    'zh': 'Chinese'
}

OPENAI_MODEL_LISTS = ["gpt-3.5-turbo", "gpt-4"]
SPACY_MODEL_LISTS = ["ja", "en", "ja_core_news_sm", "ja_core_news_md"]

class CoreProcess:
    def __init__(self, spacy_model_name = 'ja_core_news_md', openai_model_name : str = 'gpt-4'):
        try:
            if spacy_model_name not in SPACY_MODEL_LISTS:
                raise ValueError(
                f"Could not use this spacy model `{openai_model_name}`. "
                f"Please use a model in {OPENAI_MODEL_LISTS}."
            ) 
            if openai_model_name not in OPENAI_MODEL_LISTS:
                raise ValueError(
                f"Could not use this openai model `{openai_model_name}`. "
                f"Please use a model in {OPENAI_MODEL_LISTS}."
            ) 
            self.openai_model_name = openai_model_name
            self.spacy_model_name = spacy_model_name
            self.nlp = spacy.load(spacy_model_name) # load the Japanese language model with word vectors for similarity comparison
            self.similarity_threshold = 0.85 # will be used in future
        except ValueError as error:
            error_message = f"error in __init__() : {error}"
            print(error_message)
    
    def process_translation(self, df, input_sentences):
        # add the sentencizer component to the pipeline
        self.nlp.add_pipe('sentencizer')
        
        # apply sentence segmentation to the 'jp' column
        df['jp_sentences'] = df['jp'].apply(self._sentence_segmentation)

        # flatten the list of sentences from the DataFrame and create a corresponding list of Vietnamese translations
        all_sentences = [sent for sublist in df['jp_sentences'] for sent in sublist]
        
        # currently prefered to get the data in the 'vn (updated)' column
        # only if there are no data in the 'vn (updated)' column, get the data in the 'vn (original)' column 
        all_translations = [
            df['vn (updated)'].iloc[i] if pd.notna(df['vn (updated)'].iloc[i]) and df['vn (updated)'].iloc[i].strip() != "" 
            else df['vn (original)'].iloc[i]
            for i, sublist in enumerate(df['jp_sentences']) for _ in sublist
        ]

        final_translations = []
        tmplogs = []

        for input_sentence in input_sentences:
            if input_sentence.strip(): 
                # find the most similar sentence from the database and get the corresponding Vietnamese translation
                highest_similarity, most_similar_sentence, vietnamese_translation = self._find_most_similar_sentence_and_translation(input_sentence, all_sentences, all_translations)

                # fallback to ChatGPT if no suitable match is found
                if vietnamese_translation is None:
                    vietnamese_translation = self._translate_with_chatgpt(input_sentence)
                    
                final_translations.append(vietnamese_translation)
                tmplogs.append(f"input_sentence: {input_sentence}\nhighest_similarity: {highest_similarity}\nmost_similar_sentence: {most_similar_sentence}\nvietnamese_translation: {vietnamese_translation}\n")
                print("Input Sentence: ", input_sentence)                
                print("highest_similarity: ", highest_similarity)
                print("Most Similar Sentence: ", most_similar_sentence if most_similar_sentence else "No suitable match found")
                print("Vietnamese Translation: ", vietnamese_translation)
                print()
            
        return {"data": '\n'.join(final_translations), "logs": '\n'.join(tmplogs)}
        
    def read_input_text_and_get_sentences(self, input_text_file: str):
        if is_file_descriptor(input_text_file) or is_file_path(input_text_file):
            with open(input_text_file, 'r', encoding='utf-8') as file: # currently .txt file
                input_text = file.read()
        else:
            input_text = input_text_file
            
        # remove the "※" symbol from the input text (might not necessary but added the filter)
        input_text = input_text.replace("※", "") 
        input_sentences = self._sentence_segmentation(input_text)
        
        return input_sentences
    
    def set_matching_db_file(self, file):
        df = pd.read_excel(file)
        return df

    def _sentence_segmentation(self, text):
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]
    
    def _find_most_similar_sentence_and_translation(self, input_sentence, sentence_list, translations, threshold=0.85):
        input_doc = self.nlp(input_sentence)
        similarities = []
        for sent in sentence_list:
            sent_doc = self.nlp(sent)
            if input_doc.vector_norm and sent_doc.vector_norm:  # check if both vectors are non-empty
                similarity = input_doc.similarity(sent_doc)
                similarities.append((sent, similarity))
            else:
                similarities.append((sent, 0.0))  # assign zero similarity if one of the vectors is empty
        
        most_similar_sentence, highest_similarity = max(similarities, key=lambda item: item[1])
        if highest_similarity >= threshold:
            translation = translations[sentence_list.index(most_similar_sentence)]
            return highest_similarity, most_similar_sentence, translation
        else:
            return None, None, None
    
    def _translate_with_chatgpt(self, text, frLang = 'jp', toLang = 'vm'):
        # currently commented out the actual ChatGPT calling part
        return '[This will be chatgpt\'s translation result.]'
        prompt = 'Translate the following %s to %s.\n\n' % (languages[frLang], languages[toLang]) + text

        completion = client.chat.completions.create(
            model = self.openai_model_name,
            # Change the prompt parameter to the messages parameter
            messages = [
                {'role': 'user',
                #'content': s['_in'] % (s[toLang], text),
                'content': prompt,
                }
            ],
            temperature = 0  
        )
        return completion.choices[0].message.content
