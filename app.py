from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import altair as alt
import time
import pandas as pd
import json

import random
from vega_datasets import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    occurence = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    time_diff = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Task %r>" % self.id


@app.route('/', methods=['POST', 'GET'])
def index():

    occ = 0

    if request.method == 'POST':
        employee_name = request.form['content']

        tasks = Task.query.order_by(Task.date_created).all()

        names = []

        for task in tasks:
            names.append(task.content)

        occ = names.count(employee_name)

        new_entry = Task(content=employee_name,
                        occurence=occ)

        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue creating the occurence."

    else:
        tasks = Task.query.order_by(Task.date_created).all()
        return render_template('index.html', 
                                tasks = tasks,
                                chart=graph())

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Task.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return "There was a problem deleting."

# @app.route('/start/<int:id>', methods=['GET', 'POST'])
# def start(id):

#     task = Task.query.get_or_404(id)
#     try:
#         start = datetime.now()
#         return redirect('/')
    
#     except:
#         return "There was a problem starting the timer"
    
@app.route('/end/<int:id>', methods = ['GET', 'POST'])
def end(id):

    task = Task.query.get_or_404(id)

    if request.method == 'POST':

        try:
            end = datetime.utcnow()
            diff = end - task.date_created
            diff = diff.total_seconds()
            task.time_diff = diff
            db.session.commit()

            return redirect('/')
        
        except:
            return "There was a problem ending the timer"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating.'

    else:
        return render_template('update.html', task=task)



cars = data.cars()
# alt.renderers.enable('default')

WIDTH = 450
HEIGHT = 150

@app.route('/chart')
def graph():

    tasks = Task.query.order_by(Task.date_created).all()

    names = []
    dates = []
    times = []
    index = []

    for task in tasks:
        names.append(task.content)
        dates.append(str(task.date_created.date()))
        times.append(task.time_diff)
        index.append(task.occurence)

    df = pd.DataFrame({"Ind": index, 
                    "Name": names, 
                    "Date": dates, 
                    "Time": times})
    
    chart = alt.Chart(
        data=df,
        height=HEIGHT,
        width=WIDTH
        ).mark_line().encode(

    x = alt.X('Ind:Q'),
    y = alt.Y('Time:Q'),
    color = alt.Color('Name:N')

    ).interactive()

    return chart.to_json()

if __name__ == "__main__":
    app.run(debug=True)