import shelve

class ShelveStore:
    def __init__(self, filename='mydata.db'):
        self.filename = filename

    def set(self, key, value):
        with shelve.open(self.filename, writeback=True) as db:
            db[key] = value

    def get(self, key, default=None):
        with shelve.open(self.filename) as db:
            return db.get(key, default)

    def delete(self, key):
        with shelve.open(self.filename, writeback=True) as db:
            if key in db:
                del db[key]
                return True
            return False
