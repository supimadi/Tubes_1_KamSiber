from flask import Flask, make_response, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import bleach
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

PIN_AUTH = "a320480f534776bddb5cdb54b1e93d210a3c7d199e80a23c1b2178497b184c76"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()

    tempelate = render_template('index.html', students=students)
    respone = make_response(tempelate)

    respone.set_cookie("PIN_AUTH", PIN_AUTH, samesite="Strict")

    return respone

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    
    # Sanitasi input menggunakan bleach
    name = bleach.clean(name)
    grade = bleach.clean(grade)

    #Mencegah form grade menerima angka
    grade = request.form.get("grade")

    if not re.fullmatch(r"^[A-F][+-]?$", grade):
        return "Invalid grade. Only A-F with optional + or - is allowed.", 400


    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


# @app.route('/delete/<string:id>') kode sebelumnya
# def delete_student(id): kode sebelumnya
@app.route('/delete/<int:student_id>') 
def delete_student(student_id):
    # RAW Query
    # db.session.execute(text(f"DELETE FROM student WHERE id={id}")) kode sebelumnya
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    edit_student = Student.query.get_or_404(id)
    if request.method == 'POST':
        # name = request.form['name'] kode sebelumnya
        # age = request.form['age'] kode sebelumnya
        # grade = request.form['grade'] kode sebelumnya
        edit_student.name = request.form['name']
        edit_student.age = request.form['age']
        edit_student.grade = request.form['grade']
        
        # RAW Query
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}")) kode sebelumnya
        db.session.execute(text(f"UPDATE student SET name='{edit_student.name}', age={edit_student.age}, grade='{edit_student.grade}' WHERE id={edit_student.id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

