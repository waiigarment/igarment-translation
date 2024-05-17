import cherrypy
# from repositories.UserRepository import UserRepository
from database import create_store
import os
from services import UserWebService, TranslationService
from os.path import abspath

def setup_database():
    cherrypy.request.db = create_store()

if __name__ == '__main__':
    cherrypy.tools.db = cherrypy.Tool('before_handler', setup_database, priority=20)
    cherrypy.config.update({
        'tools.db.on': True,
        'server.socket_host': '0.0.0.0', 
        'server.socket_port': 8080,             
        # 'cors.expose.on': True                 
        })
    print('static root path ', os.path.abspath(os.getcwd()))
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    # cherrypy.tree.mount(UserWebService(), '/', config=conf)
    cherrypy.tree.mount(TranslationService(), '/', config=conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
