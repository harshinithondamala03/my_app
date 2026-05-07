
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

DB = SQLAlchemy(app)

class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(100), unique=True)
    password = DB.Column(DB.String(100))

class Project(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100))

class Task(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(100))
    status = DB.Column(DB.String(20), default='Pending')
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id'))

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username=username, password=password)
        DB.session.add(user)
        DB.session.commit()

        flash('Registration Successful')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid Credentials')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        project_name = request.form['project_name']
        task_title = request.form['task_title']

        project = Project(name=project_name)
        DB.session.add(project)
        DB.session.commit()

        task = Task(title=task_title, project_id=project.id)
        DB.session.add(task)
        DB.session.commit()

    tasks = Task.query.all()

    completed = Task.query.filter_by(status='Completed').count()
    pending = Task.query.filter_by(status='Pending').count()

    return render_template(
        'dashboard.html',
        tasks=tasks,
        completed=completed,
        pending=pending
    )

@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get(id)
    task.status = 'Completed'
    DB.session.commit()
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get(id)
    DB.session.delete(task)
    DB.session.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        DB.create_all()
    app.run(debug=True)
