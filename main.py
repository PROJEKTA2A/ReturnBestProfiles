import asyncio, os, requests, docx, textract # pip install python-docx, textract
from flask import Flask, request # pip install flask
from threading import Thread
from werkzeug.utils import secure_filename

app = Flask('File Reader')
app.config['UPLOAD_FOLDER'] = './uploaded_files'


@app.route('/')
def home():
  return {"File" : "Reader"}

@app.route('/fileToString', methods=['POST'])
def fileToString():
  if 'file' not in request.files:
    return {"error" : "file not uploaded", "expected" : "'file' as key for a pdf file"}
  file = request.files['file']
  filename = secure_filename(file.filename)
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
  file.save(file_path)
  
  if filename.endswith(".docx"):
    # Methode von Stackoverflow:
    # https://stackoverflow.com/questions/29309085/read-docx-files-via-python
    doc = docx.Document(file)
    allText = ""
    for docpara in doc.paragraphs:
        allText += " " + docpara.text
  elif filename.endswith(".pdf"):
    # Methode von Stackoverflow:
    # https://stackoverflow.com/questions/45795089/how-can-i-read-pdf-in-python
    allText = textract.process(file_path, method='pdfminer')
  else: 
    allText = "unsupported File Type"
  os.remove(file_path)
  return allText

def run():
  app.run(host='0.0.0.0',port=8080)

def start():
    t = Thread(target=run)
    t.start()

start()
  
""" Tests:
with open('stammdaten.pdf', 'rb') as f:
    r = requests.post("https://file-reader.shigeocst.repl.co/fileToString", files={'file': f})
print(r.text)

with open('BspAusschreibung.docx', 'rb') as f:
    r = requests.post("https://file-reader.shigeocst.repl.co/fileToString", files={'file': f})
print(r.text)
"""