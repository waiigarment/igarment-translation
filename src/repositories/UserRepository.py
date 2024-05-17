from models import User
from . import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, store):
        super().__init__(store, User)

