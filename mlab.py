import mongoengine

# mongodb://ytdownload:dinhtien12@ds159273.mlab.com:59273/sscoca-ytdl

host = "ds159273.mlab.com"
port = 59273
db_name = "sscoca-ytdl"
user_name = "ytdownload"
password = "dinhtien12"

def connect():
    mongoengine.connect(
        db_name, 
        host=host, 
        port=port, 
        username=user_name, 
        password=password
    )