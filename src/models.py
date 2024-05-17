from storm.locals import *

class User(object):
    __storm_table__ = 'users'
    id = Int(primary=True)
    username = Unicode()
    email = Unicode()

def create_schema(store):
    store.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT)")
