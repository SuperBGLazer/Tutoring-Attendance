from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import csv
from io import StringIO
from datetime import datetime
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@db/attendance_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Association Table for Many-to-Many between Student and Class
student_class = db.Table('student_class',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    classes = db.relationship('Class', secondary=student_class, back_populates='students')

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    students = db.relationship('Student', secondary=student_class, back_populates='classes')
    sessions = db.relationship('Session', backref='class_', lazy=True)

    def __repr__(self):
        return self.name

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)  # Added end_time field
    description = db.Column(db.Text, nullable=True)
    attendances = db.relationship('Attendance', backref='session', lazy=True)

    def __repr__(self):
        return f'Session on {self.date_time} - {self.end_time} for class {self.class_.name}'


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    attended = db.Column(db.Boolean, default=False)

    student = db.relationship('Student')

    def __repr__(self):
        return f'{self.student} attended {self.session}'

# Routes
@app.route('/')
def index():
    return redirect(url_for('list_classes'))

# Classes routes
@app.route('/classes')
def list_classes():
    classes = Class.query.order_by(Class.name).all()
    return render_template('list_classes.html', classes=classes)

@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        name = request.form['name']
        new_class = Class(name=name)
        try:
            db.session.add(new_class)
            db.session.commit()
            flash('Class added successfully!', 'success')
            return redirect(url_for('list_classes'))
        except IntegrityError:
            db.session.rollback()
            flash('Class with this name already exists.', 'danger')
            return redirect(request.url)
    return render_template('add_class.html')

@app.route('/classes/<int:class_id>')
def view_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    return render_template('view_class.html', class_obj=class_obj)

@app.route('/classes/<int:class_id>/edit', methods=['GET', 'POST'])
def edit_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        class_obj.name = request.form['name']
        try:
            db.session.commit()
            flash('Class updated successfully!', 'success')
            return redirect(url_for('view_class', class_id=class_id))
        except IntegrityError:
            db.session.rollback()
            flash('Class with this name already exists.', 'danger')
            return redirect(request.url)
    return render_template('edit_class.html', class_obj=class_obj)

@app.route('/classes/<int:class_id>/delete', methods=['POST'])
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    db.session.delete(class_obj)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('list_classes'))

# Student routes
@app.route('/students')
def list_students():
    students = Student.query.order_by(Student.last_name, Student.first_name).all()
    return render_template('list_students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    classes = Class.query.order_by(Class.name).all()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        class_ids = request.form.getlist('classes')
        new_student = Student(first_name=first_name, last_name=last_name, email=email)
        for class_id in class_ids:
            class_obj = Class.query.get(class_id)
            new_student.classes.append(class_obj)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('list_students'))
        except IntegrityError:
            db.session.rollback()
            flash('A student with this email already exists.', 'danger')
            return redirect(request.url)
    return render_template('add_student.html', classes=classes)

@app.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    classes = Class.query.order_by(Class.name).all()
    if request.method == 'POST':
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.email = request.form['email']
        class_ids = request.form.getlist('classes')
        student.classes = []
        for class_id in class_ids:
            class_obj = Class.query.get(class_id)
            student.classes.append(class_obj)
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('list_students'))
        except IntegrityError:
            db.session.rollback()
            flash('A student with this email already exists.', 'danger')
            return redirect(request.url)
    return render_template('edit_student.html', student=student, classes=classes)

@app.route('/students/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('list_students'))

# Import students into a class
@app.route('/classes/<int:class_id>/import_students', methods=['GET', 'POST'])
def import_students(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash('No file selected', 'danger')
            return redirect(request.url)
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        for row in csv_input:
            if not row:
                continue  # skip empty lines
            name = row[0].strip()
            if len(row) < 2 or not row[1].strip():
                flash(f'Email missing for student {name}.', 'warning')
                continue
            email = row[1].strip()
            if ',' in name:
                # Format: Last, First
                last_name, first_name = [x.strip() for x in name.split(',', 1)]
            else:
                # Format: First Last
                parts = name.strip().split()
                if len(parts) >= 2:
                    first_name = parts[0]
                    last_name = ' '.join(parts[1:])
                else:
                    first_name = parts[0]
                    last_name = ''
            try:
                existing_student = Student.query.filter_by(email=email).first()
                if existing_student:
                    # Add to class if not already in class
                    if class_obj not in existing_student.classes:
                        existing_student.classes.append(class_obj)
                        db.session.commit()
                else:
                    student = Student(first_name=first_name, last_name=last_name, email=email)
                    student.classes.append(class_obj)
                    db.session.add(student)
                    db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(f'Student {first_name} {last_name} with email {email} could not be added.', 'warning')
        flash('Students imported successfully!', 'success')
        return redirect(url_for('view_class', class_id=class_id))
    return render_template('import_students.html', class_obj=class_obj)

# Session routes
@app.route('/classes/<int:class_id>/create_session', methods=['GET', 'POST'])
def create_session(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        date_time_str = request.form['date_time']
        end_time_str = request.form['end_time']
        description = request.form['description']
        date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        session = Session(date_time=date_time, end_time=end_time, description=description, class_id=class_id)
        db.session.add(session)
        db.session.commit()
        # Create attendance records for all students in the class
        students = class_obj.students
        for student in students:
            attendance = Attendance(session_id=session.id, student_id=student.id)
            db.session.add(attendance)
        db.session.commit()
        flash('Session created successfully!', 'success')
        return redirect(url_for('mark_attendance', session_id=session.id))
    return render_template('create_session.html', class_obj=class_obj)


@app.route('/mark_attendance/<int:session_id>', methods=['GET', 'POST'])
def mark_attendance(session_id):
    session_obj = Session.query.get_or_404(session_id)
    class_obj = session_obj.class_
    if request.method == 'POST':
        attendance_ids = request.form.getlist('attendance')
        for attendance in session_obj.attendances:
            attendance.attended = str(attendance.id) in attendance_ids
        db.session.commit()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('view_session', session_id=session_obj.id))
    students = class_obj.students
    attendance_records = {a.student_id: a for a in session_obj.attendances}
    return render_template('mark_attendance.html', session=session_obj, students=students, attendance_records=attendance_records)

@app.route('/session/<int:session_id>')
def view_session(session_id):
    session_obj = Session.query.get_or_404(session_id)
    return render_template('view_session.html', session=session_obj)

@app.route('/classes/<int:class_id>/sessions')
def list_sessions(class_id):
    class_obj = Class.query.get_or_404(class_id)
    sessions = Session.query.filter_by(class_id=class_id).order_by(Session.date_time.desc()).all()
    return render_template('list_sessions.html', sessions=sessions, class_obj=class_obj)

@app.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    session_obj = Session.query.get_or_404(session_id)
    if request.method == 'POST':
        date_time_str = request.form['date_time']
        end_time_str = request.form['end_time']
        description = request.form['description']
        session_obj.date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
        session_obj.end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        session_obj.description = description
        db.session.commit()
        flash('Session updated successfully!', 'success')
        return redirect(url_for('view_session', session_id=session_obj.id))
    return render_template('edit_session.html', session=session_obj)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
