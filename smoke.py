import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from database import Database

db = Database(base_dir=os.path.dirname(__file__))
print('SHOW TABLES ->', db.execute('SHOW TABLES'))
print('CREATE TABLE ->', db.execute('CREATE TABLE test (id int, name str)'))
print('INSERT ->', db.execute("INSERT INTO test (id, name) VALUES (1, 'Alice')"))
print('SELECT ->', db.execute('SELECT * FROM test LIMIT 5'))
