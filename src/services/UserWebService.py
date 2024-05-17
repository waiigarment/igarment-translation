import cherrypy
from repositories.UserRepository import UserRepository
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class UserWebService:
    
    @cherrypy.expose
    def hee(self):
        return open(os.path.join(BASE_DIR, 'templates/index.html'))
        
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET']) 
    @cherrypy.tools.json_out()
    def index(self):
        store = cherrypy.request.db
        user_repository = UserRepository(store)
        users = user_repository.get_all()
        return [dict(id=user.id, username=user.username, email=user.email) for user in users]

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def create(self):
        data = cherrypy.request.json
        username = data.get('username')
        email = data.get('email')
        if not username or not email:
            raise cherrypy.HTTPError(400, 'Missing username or email')
        
        store = cherrypy.request.db
        user_repository = UserRepository(store)
        user = user_repository.create({"username": username, "email": email})
        return dict(id=user.id, username=user.username, email=user.email)
        return {'id': user.id, 'username': user.username, 'email': user.email}

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def update(self, id):
        data = cherrypy.request.json
        username = data.get('username')
        email = data.get('email')
        if not username or not email:
            raise cherrypy.HTTPError(400, 'Missing username or email')
        
        store = cherrypy.request.db
        user_repository = UserRepository(store)
        user = user_repository.update(int(id), {"username": username, "email": email})
        if user:
            return dict(id=user.id, username=user.username, email=user.email)
        else:
            raise cherrypy.HTTPError(404, 'User not found')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def delete(self, id):
        store = cherrypy.request.db
        user_repository = UserRepository(store)
        if user_repository.delete(int(id)):
            return {'message': 'User deleted successfully'}
        else:
            raise cherrypy.HTTPError(404, 'User not found')