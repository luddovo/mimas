import bsddb3 as bsddb

class BerkeleyDBStore:
    def __init__(self, filename):
        """Initialize the Berkeley DB with a file."""
        self.db = bsddb.hashopen(filename, 'c')  # 'c' means create if not exists

    def set(self, key, value):
        """Store a key-value pair."""
        # Keys and values must be bytes in Berkeley DB
        self.db[key.encode('utf-8')] = value.encode('utf-8')

    def get(self, key):
        """Retrieve a value by key."""
        try:
            return self.db[key.encode('utf-8')].decode('utf-8')
        except KeyError:
            return None

    def delete(self, key):
        """Delete a key-value pair."""
        try:
            del self.db[key.encode('utf-8')]
        except KeyError:
            pass

    def close(self):
        """Close the database."""
        self.db.close()

    def __enter__(self):
        """Support for context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the database is closed when exiting context."""
        self.close()

# Example usage
if __name__ == "__main__":
    # Use the store with a context manager
    with BerkeleyDBStore('mystore.db') as store:
        # Set some key-value pairs
        store.set('name', 'Alice')
        store.set('age', '30')
        
        # Retrieve values
        print(store.get('name'))  # Output: Alice
        print(store.get('age'))   # Output: 30
        print(store.get('city'))  # Output: None
        
        # Delete a key
        store.delete('age')
        print(store.get('age'))   # Output: None

    # Reopen to demonstrate persistence
    with BerkeleyDBStore('mystore.db') as store:
        print(store.get('name'))  # Output: Alice
        print(store.get('age'))   # Output: None