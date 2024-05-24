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

    def __call__(self, doc):
        translated_sentences = []
        
        for sent in doc.sents:
            sentence = sent.text.strip()
            sent
            # print('sentence ', sentence)
            if sentence in self.translation_dict:
                translated = self.translation_dict[sentence]
                sent._.translated_with_chatgpt = False
            else:
                translated = translate_with_openai(sentence)
                sent._.translated_with_chatgpt = True
            translated_sentences.append(translated)
            sent._.translated_text = translated

        # doc._.translated_text = '\n'.join(translated_sentences)
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

if not Span.has_extension("translated_with_chatgpt"):
    Span.set_extension("translated_with_chatgpt", default=None)
    
# if not Doc.has_extension("translated_text"):
#     Doc.set_extension("translated_text", default=None)

if "translation_component" not in spacy.registry.factories:
    @Language.factory("translation_component", default_config={"translation_dict": {}})
    def create_translation_component(nlp, name, translation_dict):
        return TranslationComponent(translation_dict)
