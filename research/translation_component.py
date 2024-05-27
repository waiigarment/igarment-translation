import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span
import srsly
from spacy.util import ensure_path
from openai_translation import translate_with_openai

class TranslationComponent:
    def __init__(self, translation_dict={}):
        # print('init ...................')
        self.translation_dict = translation_dict

    # def __call__(self, doc):
    #     translated_sentences = []
        
    #     for sent in doc.sents:
    #         sentence = sent.text.strip()
    #         print('sentence ', sentence)
    #         if sentence in self.translation_dict:
    #             translated = self.translation_dict[sentence]
    #             sent._.translated_with_chatgpt = False
    #         else:
    #             translated = translate_with_openai(sentence)
    #             sent._.translated_with_chatgpt = True
    #         translated_sentences.append(translated)
    #         sent._.translated_text = translated

    #     # doc._.translated_text = '\n'.join(translated_sentences)
    #     return doc
    def __call__(self, doc):
        translated_sentences = []
        sentences = [sent for sent in doc.sents if sent.text.strip() and not all(char in '、' for char in sent.text.strip())]
        n = len(sentences)

        i = 0
        while i < n:
            sentence = sentences[i].text.strip()
            # print('sentence ', sentence)
            # First, check if the sentence itself is in the translation dictionary
            if sentence in self.translation_dict:
                translated = self.translation_dict[sentence]
                sentences[i]._.translated_with_chatgpt = False                
            else:
                combined_sentence = None
                combined_translation = None

                # Try to combine with the next sentence
                if i + 1 < n:
                    combined_sentence_list = [
                        sentence + ' ' + sentences[i + 1].text.strip(),
                        sentence + '、' + sentences[i + 1].text.strip(),
                        sentence + ' 、' + sentences[i + 1].text.strip(),
                        
                        sentence + ' ' + sentences[i + 1].text.strip().rstrip('、'),
                        sentence + ' ' + sentences[i + 1].text.strip().lstrip('、'),
                        
                        sentence.rstrip('、') + ' ' + sentences[i + 1].text.strip().rstrip('、'),
                        sentence.rstrip('、') + ' ' + sentences[i + 1].text.strip().lstrip('、'),
                        
                        sentence.lstrip('、') + ' ' + sentences[i + 1].text.strip().rstrip('、'),
                        sentence.lstrip('、') + ' ' + sentences[i + 1].text.strip().lstrip('、'),
                    ]
                    # combined_sentence = sentence + ' ' + sentences[i + 1].text.strip()
                    for e in combined_sentence_list:
                        # print('combined_sentence with next', e)
                        if e in self.translation_dict:
                            combined_sentence = e
                            sentences[i]._.combined_sentence = combined_sentence
                            
                            combined_translation = self.translation_dict[combined_sentence]
                            sentences[i]._.translated_with_chatgpt = False
                            sentences[i]._.translated_with_chatgpt = False
                            sentences[i]._.translated_text = combined_translation
                            sentences[i]._.combined_translated_text = combined_translation
                            translated = combined_translation
                            i += 1  # Skip the next sentence
                        
                        
                # Try to combine with the previous sentence if no combined translation found with next
                if combined_translation is None and i - 1 >= 0:
                    # combined_sentence = sentences[i - 1].text.strip() + ' ' + sentence
                    combined_sentence_list = [
                        sentences[i - 1].text.strip() + ' ' + sentence,
                        sentences[i - 1].text.strip() + '、' + sentence,
                        sentences[i - 1].text.strip() + ' 、' + sentence,
                        
                        sentences[i - 1].text.strip() + ' ' + sentence.rstrip('、'),
                        sentences[i - 1].text.strip() + ' ' + sentence.lstrip('、'),
                        
                        sentences[i - 1].text.strip().rstrip('、') + ' ' + sentence.rstrip('、'),
                        sentences[i - 1].text.strip().rstrip('、') + ' ' + sentence.lstrip('、'),
                        
                        sentences[i - 1].text.strip().lstrip('、') + ' ' + sentence.rstrip('、'),
                        sentences[i - 1].text.strip().lstrip('、') + ' ' + sentence.lstrip('、'),

                    ]
                    for e in combined_sentence_list:
                        # print('combined_sentence with previous', e)
                        if e in self.translation_dict:
                            combined_sentence  = e
                            sentences[i]._.combined_sentence = combined_sentence
                            
                            combined_translation = self.translation_dict[combined_sentence]
                            sentences[i]._.translated_with_chatgpt = False
                            sentences[i]._.translated_with_chatgpt = False
                            sentences[i]._.translated_text = combined_translation
                            sentences[i]._.combined_translated_text = combined_translation
                            # Update the previous sentence translation and skip setting for current sentence
                            translated = combined_translation

                if combined_translation is None:
                    # Translate separately if no combined translation found
                    translated = translate_with_openai(sentence)
                    sentences[i]._.translated_with_chatgpt = True

            translated_sentences.append(translated)
            sentences[i]._.translated_text = translated
            i += 1

        return doc

    def add_translation(self, original, translated):
        original = original.strip()
        translated = translated.strip()
        self.translation_dict[original] = translated

    def to_disk(self, path, exclude=tuple()):
        path = ensure_path(path)
        if not path.exists():
            path.mkdir()
        srsly.write_json(path / "translation_dict.json", self.translation_dict)

    def from_disk(self, path, exclude=tuple()):
        self.translation_dict = srsly.read_json(path / "translation_dict.json")
        return self
    
if not Span.has_extension("translated_text"):
    Span.set_extension("translated_text", default=None)

if not Span.has_extension("combined_sentence"):
    Span.set_extension("combined_sentence", default=None)
    
if not Span.has_extension("combined_translated_text"):
    Span.set_extension("combined_translated_text", default=None)
    
if not Span.has_extension("translated_with_chatgpt"):
    Span.set_extension("translated_with_chatgpt", default=None)
    
# if not Doc.has_extension("translated_text"):
#     Doc.set_extension("translated_text", default=None)

if "translation_component" not in spacy.registry.factories:
    @Language.factory("translation_component", default_config={"translation_dict": {}})
    def create_translation_component(nlp, name, translation_dict):
        return TranslationComponent(translation_dict)
