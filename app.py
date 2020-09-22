from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import altair as alt
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    time_diff = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Task %r>" % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue creating the task."

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks = tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return "There was a problem deleting."

# @app.route('/start/<int:id>', methods=['GET', 'POST'])
# def start(id):

#     task = Todo.query.get_or_404(id)
#     try:
#         start = datetime.now()
#         return redirect('/')
    
#     except:
#         return "There was a problem starting the timer"
    
@app.route('/end/<int:id>', methods = ['GET', 'POST'])
def end(id):

    task = Todo.query.get_or_404(id)

    if request.method == 'POST':

        try:
            end = datetime.utcnow()
            diff = end - task.date_created
            diff = diff.total_seconds()
            task.time_diff = diff
            db.session.commit()
            print("Blah")

            return redirect('/')
        
        except:
            return "There was a problem ending the timer"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating.'
        
    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)