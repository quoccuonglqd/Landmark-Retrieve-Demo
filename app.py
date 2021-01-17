from flask import Flask, request, jsonify, make_response, render_template
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS, IMAGES
from werkzeug import secure_filename
from color_descriptor import *
import argparse
import cv2
import os.path as osp
import os

import time


app = Flask(__name__)

docs = UploadSet('datafiles', DOCUMENTS)
app.config['UPLOADED_DATAFILES_DEST'] = '/static/uploads'
app.config['UPLOAD_FOLDER'] = '/static/uploads'

configure_uploads(app, docs)
cd = ColorDescriptor((8, 12, 3))

# @app.route('/')
# def home():
#     print("hello")
#     return render_template('index.html')

@app.route('/', methods=['GET','POST'])
def upload():
    #myFiles is the name value in input element
    if request.method == 'POST' and 'myFiles' in request.files:
        # print(request.files['myFiles'].filename)
        file = request.files['myFiles']
        filename = secure_filename(file.filename)
        file.save("D:/web_dev/static/uploads/"+ filename)

        query_res = search_image("D:/web_dev/static/uploads/"+ filename)
        
        return render_template('index.html', imgpath = {
            'data':[x[0] for x in query_res],
            'data1':[x[1] for x in query_res],
            'isremove':True,
            'req_path':"/static/uploads/"+ filename})
    return render_template('index.html', imgpath = {'data':[],'data1':[],'isremove':False,'req_path':""})
    #return None

if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 5000, debug=True)

# # loop over the results
# for (score, resultID) in results:
#     # load the result image and display it
#     result = cv2.imread(args["result_path"] + "/" + resultID)
#     cv2.imshow("Result", result)
#     cv2.waitKey(0)