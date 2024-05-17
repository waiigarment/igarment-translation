from storm.locals import create_database, Store
from models import create_schema

DATABASE_PATH = 'sqlite:///users.db'
def get_database():
    return create_database(DATABASE_PATH)

def create_store():
    database = get_database()
    store = Store(database)
    create_schema(store)
    return store
