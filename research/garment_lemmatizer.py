import spacy
from spacy.language import Language
from spacy.tokens import Doc
from spacy.tokens import Token

class GarmentLemmatizer:
    def __init__(self, garment_terms):
        self.garment_terms = set(garment_terms)  

    def __call__(self, doc):
        for token in doc:
            if token.text in self.garment_terms:
                token.lemma_ = token.text  
            else:
                token.lemma_ = token.text 
        return doc

if not Token.has_extension("lemma_"):
    Token.set_extension("lemma_", default="", force=True)

@Language.factory("garment_lemmatizer", default_config={"garment_terms": []})
def create_garment_lemmatizer(nlp, name, garment_terms):
    return GarmentLemmatizer(garment_terms)