import os, requests
from flask import Flask, request # pip install flask
from flask_cors import CORS
from threading import Thread
from werkzeug.utils import secure_filename

app = Flask('ReturnBestProfiles')
CORS(app)
app.config['UPLOAD_FOLDER'] = './uploaded_files'

@app.route('/')
def home():
  return {"Best" : "Profiles"}

@app.route('/returnBestProfiles', methods=['POST'])
def returnBestProfiles():
  if 'file' not in request.files:
    return {"error" : "file not uploaded", "expected" : "'file' as key for a pdf file"}
  file = request.files['file']
  filename = secure_filename(file.filename)
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
  file.save(file_path)

  # Dokument auslesen:
  with open(file_path, "rb") as f:
    Text = requests.post("https://replit.com/@shigeocst/file-reader/fileToString", data={"file" : f}).text

  # DbDecidaloMap aus Text machen:
  data={"text" : Text}
  DbDecidaloMap = requests.post("https://stringtodbdecidalomap.shigeocst.repl.co/StringToDbDecidaloMap", data=data)

  ListOfProfileMaps = []
  profile_ids = 5
  # Scorer aufrufen für alle Profile
  for i in range(profile_ids):
    ListOfProfileMaps.append(requests.post("https://scorer.shigeocst.repl.co/Scorer", data={"ProfileID" : i, "DbDecidaloMap" : DbDecidaloMap}).json())

  os.remove(file_path)
  # Liste sortiert zurückgeben
  return sorted(ListOfProfileMaps, key=lambda x: x['Score'], reverse=True)


def run():
  app.run(host='0.0.0.0',port=8080)

def start():
    t = Thread(target=run)
    t.start()

start()