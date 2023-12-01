import os, requests, docx, textract
from flask import Flask, request
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
    return {"error" : "file not uploaded", "expected" : "'file' as key for a pdf or docx file"}
  file = request.files['file']
  file_name = secure_filename(file.filename)
  
  if not ( file_name.endswith(".pdf") or file_name.endswith(".docx") ):
    return {"error" : "unsupported file type"}
    
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
  file.save(file_path)

  # Dokument auslesen:
  allText=FileToString(file_path, file_name)
  os.remove(file_path)

  # DbDecidaloMap aus Text machen:
  data={"text" : allText}
  DbDecidaloMap = requests.post("https://stringtodbdecidalomap.shigeocst.repl.co/StringToDbDecidaloMap", data=data)

  ListOfProfileMaps = []
  profile_ids = 5
  # Scorer aufrufen für alle Profile
  for i in range(profile_ids):
    ListOfProfileMaps.append(requests.post("https://scorer.shigeocst.repl.co/Scorer", data={"ProfileID" : i, "DbDecidaloMap" : DbDecidaloMap}).json())

  # Liste sortiert zurückgeben
  return sorted(ListOfProfileMaps, key=lambda x: x['Score'], reverse=True)


def run():
  app.run(host='0.0.0.0',port=8080)

def start():
    t = Thread(target=run)
    t.start()

start()


def FileToString(file_path, file_name):
  if file_name.endswith(".docx"):
    # Stackoverflow: https://stackoverflow.com/questions/29309085/read-docx-files-via-python
    doc = docx.Document(file_path)
    allText = ""
    for docpara in doc.paragraphs:
        allText += " " + docpara.text
  else: #pdf
    # Stackoverflow: https://stackoverflow.com/questions/45795089/how-can-i-read-pdf-in-python
    allText = textract.process(file_path, method='pdfminer')
  return allText