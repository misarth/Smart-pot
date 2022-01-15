# using python 3
from os import name
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import Required
from data import PLANTS
import tensorflow as tf
import pandas as pd 
import numpy as np 
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
import cv2
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename 
from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder

import os
app = Flask(__name__)
# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
# Flask-Bootstrap requires this line
Bootstrap(app)
# this turns file-serving to static, using Bootstrap files installed in env
# instead of using a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    name = StringField('Enter the name of the plant to check its planning for the week', validators=[Required()])
    submit = SubmitField('Submit')
class ImageForm(FlaskForm):
    inp = FileField()
    sub = SubmitField("Submit")
# define functions to be used by the routes (just one here)

# retrieve all the names from the dataset and put them into a list
def get_names(source):
    names = []
    for row in source:
        name = row["Common_Name"]
        names.append(name)
    return sorted(names)

# all Flask routes below

UPLOAD_FOLDER = './images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return file.filename
# two decorators using the same function
@app.route('/', methods=['GET', 'POST'])

def upload_file():
    app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        return path

        return 'ok'
    return '''
    <h1>Upload new File</h1>
    <form action="/actor.html" method="post" enctype="multipart/form-data">
      <input type="file" name="file1">
      <input type="submit">
    </form>
    '''
@app.route('/actor.html', methods=['GET', 'POST'])
def index():
    l = ['Black-grass', 'Charlock', 'Cleavers', 'Common Chickweed',
       'Common wheat', 'Fat Hen', 'Loose Silky-bent', 'Maize',
       'Scentless Mayweed', 'Shepherds Purse',
       'Small-flowered Cranesbill', 'Sugar beet']
    lbl = LabelEncoder()
    lbl.fit(l)
    #message2 = upload_file()
    app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
    image=upload_file()
    model = load_model("./file/content/savem")
    imgbgr = cv2.imread(image)
    imgRgb = cv2.cvtColor(imgbgr, cv2.COLOR_BGR2RGB)
    training = []
    training.append(cv2.resize(imgRgb,(128,128)))
    train = np.asarray(training)
    train = train/255.0
    p = model.predict(train)
    y = np.argmax(model.predict(train),axis=1)
    nm = lbl.inverse_transform(y)
    names = get_names(PLANTS)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    formimage = ImageForm()
    message = ""
    water_needs = ""
    Climate_Zones=""
    Light_Needs=""
    Soil_Type=""
    Maintenance=""
    if form.validate_on_submit():
        name = form.name.data
        if name in names:
            for row in PLANTS:
                if name==row["Common_Name"]:
                    row_wanted=row
                    water_needs=row["Water_Needs"]
                    Climate_Zones=row["Climate_Zones"]
                    Light_Needs=row["Light_Needs"]
                    Soil_Type=row["Soil_Type"]
                    Maintenance=row["Maintenance"]
                message = "Here is what your plant really needs :" 
                msg_water = "water_needs:" + water_needs
                
            # empty the form field
                form.name.data = ""
        else:
            message = "The plant that you entered is not in our database."
    # notice that we don't need to pass name or names to the template
    return render_template('index.html', formimage= formimage,form=form, message=message,water_needs=water_needs,Climate_Zones=Climate_Zones,Light_Needs=Light_Needs,Soil_Type=Soil_Type,Maintenance=Maintenance,image = image,nm=nm[0])

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
