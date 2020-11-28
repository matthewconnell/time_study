from flask import Flask, render_template, request, redirect, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import altair as alt
import time
import pandas as pd
import numpy as np
import json
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///time_study.db'
db = SQLAlchemy(app)

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.String(200), nullable=False)
    observation = db.Column(db.Integer, default=0)
    staff = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=datetime.utcnow)
    time_diff = db.Column(db.Integer, default=0)
    item_description = db.Column(db.String(200))
    sku = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Task %r>" % self.id

@app.route('/', methods=['POST', 'GET'])
def index():

    occ = 0

    if request.method == 'POST':

        employee_name = request.form['content']
        num_staff = int(request.form['staff'])

        tasks = Task.query.order_by(Task.start_time).all()

        new_entry = Task(operator=employee_name)

        db.session.add(new_entry)
        print('1')
        db.session.commit()
        print('2')
        return redirect('/')

        # except:
        #     return "There was an issue creating the observation."

    else:
        tasks = Task.query.order_by(Task.start_time).all()
        return render_template('index.html', 
                                tasks = tasks#,
                                # chart=graph()
                                )


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Task.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return "There was a problem deleting."
    
@app.route('/end/<int:id>', methods = ['GET', 'POST'])
def end(id):

    task = Task.query.get_or_404(id)

    if request.method == 'POST':

        try:
            task.end_time= datetime.utcnow()
            diff = task.end_time - task.start_time
            task.time_diff = diff.total_seconds()
            db.session.commit()

            return redirect('/')
        
        except:
            return "There was a problem ending the timer"


def make_df():

    tasks = Task.query.order_by(Task.start_time).all()

    names = []
    dates = []
    times = []
    index = []
    observations = []

    for task in tasks:
        names.append(task.operator)
        dates.append(str(task.start_time.date()))
        times.append(task.time_diff)
        index.append(task.observation)
        observations.append(task.observation)

    df = pd.DataFrame({"Observation": index, 
                    "Name": names,
                    "Count": elements, 
                    "Date": dates, 
                    "Time": times})

    return df

@app.route('/download/csv', methods=['POST'])
def download_csv():

    df = make_df()

    df_csv = df.to_csv()

    return Response(
        df_csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=time_study.csv"})

@app.route('/download/xlsx', methods=['POST'])
def download_xlsx():

    df = make_df()

    df.to_excel('time_study.xlsx')

    return send_file('time_study.xlsx', 
                    as_attachment=True,
                    attachment_filename='time_study.xlsx')

WIDTH = 600
HEIGHT = 350

@app.route('/chart')
def graph():

    df = make_df()
    
    chart = alt.Chart(
    data=df.groupby(by=['Name', 'Observation']).mean().reset_index(),
        height=HEIGHT,
        width=WIDTH
).mark_line().encode(
    x = alt.X('Observation:Q'),
    y = alt.Y('Time:Q'),
    color = alt.Color('Name')
    ).interactive()

    return chart.to_json()

if __name__ == "__main__":
    app.run(debug=True)