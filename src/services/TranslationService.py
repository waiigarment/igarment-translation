import cherrypy
from repositories.UserRepository import UserRepository
import os
from pathlib import Path
from utils.commons import is_file_descriptor, is_file_path
from core import CoreProcess

BASE_DIR = Path(__file__).resolve().parent.parent

class TranslationService:
        
    @cherrypy.expose
    def index(self):
        return open(os.path.join(BASE_DIR, 'templates/index.html'))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, file):
        content = file.file.read().decode('utf-8')
        print('content ', content)
        return {"content": content}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def process(self, file):
        content = file.file.read().decode('utf-8')

        core_process = CoreProcess()
        
        input_sentences = core_process.read_input_text_and_get_sentences(content)

        # currently using 'syrremk_new_add reason column.xls' this file only
        df = core_process.set_matching_db_file(os.path.join(BASE_DIR, 'datafiles/syrremk_new_add reason column.xls'))

        result = core_process.process_translation(df, input_sentences)

        return {"content": result["data"], "logs": result["logs"]}
    
    