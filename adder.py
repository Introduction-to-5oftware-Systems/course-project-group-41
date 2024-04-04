
import psycopg2
from psycopg2 import Binary

db_connector = psycopg2.connect("postgresql://QES:WoPH1gwM3_JGB4Zkcovy9w@iss-group-41-4102.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/issproject?sslmode=verify-full")
user_db = db_connector.cursor()   
query = '''CREATE TABLE IF NOT EXISTS user_details (
    user_id INT PRIMARY KEY,
    username VARCHAR(200) NOT NULL UNIQUE,
    email VARCHAR(200) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    user_images INT
);
'''
user_db.execute(query)
db_connector.commit()


query = '''CREATE TABLE IF NOT EXISTS images (
    image_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    image_metadata VARCHAR(200) NOT NULL,
    image BYTEA
);'''
user_db.execute(query)
db_connector.commit()

query = '''CREATE TABLE IF NOT EXISTS audio (
    audio_id INT PRIMARY KEY,
    audio BYTEA,
    audio_metadata VARCHAR(200) NOT NULL
);'''
user_db.execute(query)
db_connector.commit()


# query = '''ALTER TABLE images DROP CONSTRAINT images_user_id_fkey;'''
# user_db.execute(query)
# db_connector.commit()

# f = open("audio1.mp3", "rb")
# binary_contents = f.read()
# insert_query = "INSERT INTO audio (audio_id, audio, audio_metadata) VALUES (%s, %s, %s)"
# audio_metadata = "audio1.mp3"
# audio_values = ("1", Binary(binary_contents), audio_metadata)
# user_db.execute(insert_query, audio_values)
# db_connector.commit()
# f.close()

# f = open("audio2.mp3", "rb")
# binary_contents = f.read()
# insert_query = "INSERT INTO audio (audio_id, audio, audio_metadata) VALUES (%s, %s, %s)"
# audio_metadata = "audio2.mp3"
# audio_values = ("2", Binary(binary_contents), audio_metadata)
# user_db.execute(insert_query, audio_values)
# db_connector.commit()
# f.close()

f = open("audio3.mp3", "rb")
binary_contents = f.read()
insert_query = "INSERT INTO audio (audio_id, audio, audio_metadata) VALUES (%s, %s, %s)"
audio_metadata = "audio3.mp3"
audio_values = ("3", Binary(binary_contents), audio_metadata)
user_db.execute(insert_query, audio_values)
db_connector.commit()
f.close()




