from pickle import POP
from flask import Flask, render_template, url_for, request, redirect, flash, send_from_directory
from flask import json
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import json
from flask_paginate import Pagination, get_page_parameter
from pdf2image import convert_from_path
import glob
import cv2
import pytesseract
from pytesseract import Output
import base64

UPLOAD_FOLDER = './uploads'
TEMP_FOLDER = './temp'
ALLOWED_EXTENSIONS = {'pdf'}
POPPLER_PATH = r"C:\Users\Paul\AppData\Local\Programs\Python\Python39\tmp\poppler\Library\bin"
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
 
@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

#    
@app.route('/')
@app.route('/<page>')
@app.route('/<page>/<total>')
def index(page=1, total=1):
    files = os.listdir(UPLOAD_FOLDER)
    files = dict.fromkeys(files)
    for key in files: 
        files[key] = 1    

    tempfiles = os.listdir(TEMP_FOLDER)
    tempfiles = dict.fromkeys(tempfiles)
    pagefiles = dict()
    tempfiles2 = os.listdir(TEMP_FOLDER)

    for key in tempfiles: 
        tempfiles[key] = 1     

    total = len(tempfiles) // 10 + 1 
    start = int((int(page) - 1) * 10)
    end = int(int(page) * 10 - 1)
 #   return start
    for key in range(start, end):
        pagefiles[tempfiles2[key]] = 1  
        #os.path.join(app.config['TEMP_FOLDER']

    pagination = Pagination(page=page, total=len(files), search='', record_name='')
    return render_template('index.html', web_data = files, page=page, total=total, temp=pagefiles)

@app.route("/temp/<filename>")
def temp(filename):
    return send_from_directory("temp", filename) 

@app.route("/recognize/<filename>", methods = ['GET', 'POST'])  
@app.route("/recognize/<filename>/<lang>", methods = ['GET', 'POST'])
def recognize(filename, lang='', page=1):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    img = cv2.imread(os.path.join(app.root_path, app.config['TEMP_FOLDER'], filename))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_string(img, lang='deu', config=config) #, output_type=Output.DICT
    datahtml = dict()
    for i, el in enumerate(data.splitlines()):
        el = el.split()
        datahtml[str(i) + ';' + ";".join(el) ]= ";".join(el) 

 #   flash('File recognized') 
    files = os.listdir(UPLOAD_FOLDER)
    files = dict.fromkeys(files) 
    for key in files:  
        files[key] = 1    

    tempfiles = os.listdir(TEMP_FOLDER)
    tempfiles = dict.fromkeys(tempfiles)
    pagefiles = dict()
    tempfiles2 = os.listdir(TEMP_FOLDER)

    for key in tempfiles: 
        tempfiles[key] = 1     

    total = len(tempfiles) // 10 + 1 
    start = int((int(page) - 1) * 10) 
    end = int(int(page) * 10 - 1)

    for key in range(start, end):
        pagefiles[tempfiles2[key]] = 1  

    return render_template('index.html', page=1, web_data = files, html_data = datahtml, total=total, temp=pagefiles, file = filename)   

@app.route('/convert/<filename>')
def convertfile(filename):
    files = glob.glob(os.path.join(app.root_path, app.config['TEMP_FOLDER'], '*.jpg'), recursive=False)
 #   return os.path.join(app.root_path, app.config['TEMP_FOLDER'], '*.jpg')
    for f in files:
        try:
            os.remove(f)
        except OSError as e: 
            print("Error: %s : %s" % (f, e.strerror))

    # Store Pdf with convert_from_path function
    images = convert_from_path(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename), poppler_path = POPPLER_PATH)
    
    for i in range(len(images)):
        # Save pages as images in the pdf
        #images[i].save('page'+ str(i) +'.jpg', 'JPEG')
        images[i].save(os.path.join(app.root_path, app.config['TEMP_FOLDER'], 'page'+ str(i) +'.jpg'), 'JPEG')

    flash('Image files created ' + str(len(images))) 
    files = os.listdir(UPLOAD_FOLDER)
    files = dict.fromkeys(files)
    for key in files:  
        files[key] = 1  
    
    return render_template('index.html', web_data = files) 
    #    return 'converting ' + file;  #render_template('index.html')
 
@app.route('/delete/<filename>')
def deletefile(filename):
    os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

#    f.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], '', f.filename))
    flash('File deleted')
    files = os.listdir(UPLOAD_FOLDER)
    files = dict.fromkeys(files)
    for key in files: 
        files[key] = 1  
    
    return render_template('index.html', web_data = files) 

    return redirect(url_for('admin_items'))       
    return 'converting ' + file;  #render_template('index.html')
"""
@app.route('/upload')
def upload_file():
  return render_template('index.html')
"""
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file(): 
   if request.method == 'POST':
        f = request.files['file']
        #FileStorage(request.stream).save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

        f.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], '', f.filename))
        flash('File uploaded')
        files = os.listdir(UPLOAD_FOLDER)
        files = dict.fromkeys(files)
        for key in files: 
            files[key] = 1    

        page = 1    
        pagination = Pagination(page=page, total=len(files), search='', record_name='')
 
        return render_template('index.html', web_data = files, pagination=pagination)
 #       return redirect(url_for('index', web_data = files))         
        #json.dumps(files)
 #     f = request.files['file']   
     
if __name__ == "__main__":  
    app.run(debug=True)    