class BaseRepository:
    def __init__(self, store, model):
        self.store = store
        self.model = model

    def get_all(self):
        return self.store.find(self.model)

    def get_by_id(self, id):
        return self.store.get(self.model, id)

    def create(self, attributes: dict):
        entity = self.model()

        for key, value in attributes.items():
            setattr(entity, key, value)

        self.store.add(entity)
        self.store.commit()
        return entity
    
    def update(self, id, attributes: dict):
        entity = self.store.get(self.model, id)
        if entity:
            for key, value in attributes.items():
                setattr(entity, key, value)
            self.store.commit()
            return entity
        else:
            return None

    def delete(self, id):
        entity = self.store.get(self.model, id)
        if entity:
            self.store.remove(entity)
            self.store.commit()
            return True
        else:
            return False