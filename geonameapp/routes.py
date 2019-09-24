from flask import render_template
from geonameapp import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/regions')
def regions():
    return render_template('regions.html')
