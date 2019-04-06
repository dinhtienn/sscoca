import mongoengine
import config

def connect(dbname):
    if dbname != config.DATABASE_CONFIG['dbname']:
        raise ValueError("Couldn't not find DB with given name")
    mongoengine.connect(
        db=config.DATABASE_CONFIG['dbname'],
        host=config.DATABASE_CONFIG['host'],
        port=config.DATABASE_CONFIG['port'],
        user=config.DATABASE_CONFIG['user'],
        password=config.DATABASE_CONFIG['password'],
    )