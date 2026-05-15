from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import random
from models import db, User, Subject, Quiz, Question, Result
from sqlalchemy import func

app = Flask(__name__)

# CONFIG
app.secret_key = "quizmaster"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()


# =========================
# LOGIN
# =========================
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['fullname'] = user.fullname
            session['role'] = user.role

            if user.role == "student":
                return redirect('/student_dashboard')

            elif user.role == "teacher":
                return redirect('/teacher_dashboard')

            elif user.role == "admin":
                return redirect('/admin_dashboard')

        return "Invalid Email or Password"

    return render_template('index.html')


# =========================
# SIGNUP
# =========================
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            return "Password does not match"

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        if role == "admin":
            return "Admin signup not allowed"

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            fullname=fullname,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    return render_template('signup.html')


# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin_dashboard')
def admin_dashboard():

    if session.get('role') != 'admin':
        return redirect('/')

    return render_template(
        'dashboard_admin.html',
        admin=User.query.get(session['user_id']),
        recent_students=User.query.filter_by(role='student').all(),
        recent_teachers=User.query.filter_by(role='teacher').all(),
        total_students=User.query.filter_by(role='student').count(),
        total_teachers=User.query.filter_by(role='teacher').count(),
        total_subjects=Subject.query.count(),
        total_users=User.query.count(),
        total_quizzes=Quiz.query.count()
    )


# =========================
# ADMIN STUDENTS
# =========================
@app.route('/admin_students')
def admin_students():

    if session.get('role') != 'admin':
        return redirect('/')

    students = User.query.filter_by(role='student').all()

    return render_template(
        'admin_students.html',
        students=students
    )


# =========================
# ADMIN TEACHERS
# =========================
@app.route('/admin_teachers')
def admin_teachers():

    if session.get('role') != 'admin':
        return redirect('/')

    teachers = User.query.filter_by(role='teacher').all()

    return render_template(
        'admin_teachers.html',
        teachers=teachers
    )


# =========================
# EDIT USER
# =========================
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get(id)

    if not user:
        return "User Not Found"

    if request.method == 'POST':

        user.fullname = request.form['fullname']
        user.email = request.form['email']
        user.role = request.form['role']

        db.session.commit()

        return redirect('/admin_students')

    return render_template(
        'edit_user.html',
        user=user
    )


# =========================
# DELETE USER
# =========================
@app.route('/delete_user/<int:id>')
def delete_user(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get(id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect('/admin_students')


# =========================
# ADD SUBJECT
# =========================
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():

    if session.get('role') != 'admin':
        return redirect('/')

    if request.method == 'POST':

        subject_name = request.form['subject_name']
        chapter_name = request.form['chapter_name']

        subject = Subject(
            subject_name=subject_name,
            chapter_name=chapter_name
        )

        db.session.add(subject)
        db.session.commit()

    return render_template(
        'add_subject.html',
        subjects=Subject.query.all()
    )

# =========================
# EDIT SUBJECT
# =========================
@app.route('/edit_subject/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):

    if session.get('role') != 'admin':
        return redirect('/')

    subject = Subject.query.get(id)

    if not subject:
        return "Subject not found"

    if request.method == 'POST':

        subject.subject_name = request.form['subject_name']

        subject.chapter_name = request.form['chapter_name']

        db.session.commit()

        return redirect('/add_subject')

    return render_template(
        'edit_subject.html',
        subject=subject
    )


# =========================
# DELETE SUBJECT
# =========================
@app.route('/delete_subject/<int:id>')
def delete_subject(id):

    if session.get('role') != 'admin':
        return redirect('/')

    subject = Subject.query.get(id)

    if not subject:
        return "Subject not found"

    db.session.delete(subject)

    db.session.commit()

    return redirect('/add_subject')

# =========================
# ASSIGN SUBJECT
# =========================
@app.route('/assign_subject', methods=['GET', 'POST'])
def assign_subject():

    if session.get('role') != 'admin':
        return redirect('/')

    teachers = User.query.filter_by(role='teacher').all()

    subjects = Subject.query.filter_by(
        teacher_id=None
    ).all()

    if request.method == 'POST':

        subject_id = request.form['subject_id']
        teacher_id = request.form['teacher_id']

        subject = Subject.query.get(subject_id)

        subject.teacher_id = teacher_id

        db.session.commit()

    return render_template(
        'assign_subject.html',
        teachers=teachers,
        subjects=subjects,
        assigned_subjects=Subject.query.filter(
            Subject.teacher_id.isnot(None)
        ).all()
    )

# =========================
# EDIT ASSIGNED SUBJECT
# =========================
@app.route('/edit_assigned_subject/<int:id>', methods=['GET', 'POST'])
def edit_assigned_subject(id):

    if session.get('role') != 'admin':
        return redirect('/')

    subject = Subject.query.get(id)

    if not subject:
        return "Subject not found"

    teachers = User.query.filter_by(role='teacher').all()

    if request.method == 'POST':

        subject.teacher_id = request.form['teacher_id']

        db.session.commit()

        return redirect('/assign_subject')

    return render_template(
        'edit_assigned_subject.html',
        subject=subject,
        teachers=teachers
    )


# =========================
# DELETE ASSIGNED SUBJECT
# =========================
@app.route('/delete_assigned_subject/<int:id>')
def delete_assigned_subject(id):

    if session.get('role') != 'admin':
        return redirect('/')

    subject = Subject.query.get(id)

    if not subject:
        return "Subject not found"

    subject.teacher_id = None

    db.session.commit()

    return redirect('/assign_subject')

# =========================
# STUDENT DASHBOARD
# =========================
@app.route('/student_dashboard')
def student_dashboard():

    if session.get('role') != 'student':
        return redirect('/')

    return render_template(
        'dashboard_student.html',
        student=User.query.get(session['user_id']),
        subjects=Subject.query.filter(
            Subject.teacher_id.isnot(None)
        ).all(),
        quizzes=Quiz.query.all()
    )


# =========================
# TEACHER DASHBOARD
# =========================
@app.route('/teacher_dashboard')
def teacher_dashboard():

    if session.get('role') != 'teacher':
        return redirect('/')

    teacher = User.query.get(session['user_id'])

    return render_template(
        'dashboard_teacher.html',
        teacher=teacher,
        subjects=Subject.query.filter_by(
            teacher_id=teacher.id
        ).all(),
        quizzes=Quiz.query.filter_by(
            teacher_id=teacher.id
        ).all()
    )


# =========================
# QUIZ DETAILS
# =========================
@app.route('/quizzes/<int:id>')
def quiz_details(id):

    subject = Subject.query.get(id)

    if not subject:
        return "Subject not found"

    quizzes = Quiz.query.filter_by(
        subject_id=id
    ).all()

    return render_template(
        'teacher_quizzes.html',
        subject=subject,
        quizzes=quizzes
    )


# =========================
# CREATE QUIZ
# =========================
@app.route('/create_quiz/<int:subject_id>', methods=['POST'])
def create_quiz(subject_id):

    if session.get('role') != 'teacher':
        return redirect('/')

    title = request.form['title']

    new_quiz = Quiz(
        title=title,
        subject_id=subject_id,
        teacher_id=session['user_id']
    )

    db.session.add(new_quiz)
    db.session.commit()

    return redirect(f'/quizzes/{subject_id}')


# =========================
# DELETE QUIZ
# =========================
@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return "Quiz not found"

    subject_id = quiz.subject_id

    db.session.delete(quiz)
    db.session.commit()

    return redirect(f'/quizzes/{subject_id}')


# =========================
# ADD QUESTION
# =========================
@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return "Quiz not found"

    if request.method == 'POST':

        new_question = Question(

            question_text=request.form['question'],

            option_a=request.form['option_a'],

            option_b=request.form['option_b'],

            option_c=request.form['option_c'],

            option_d=request.form['option_d'],

            correct_answer=request.form['correct_answer'],

            quiz_id=quiz_id
        )

        db.session.add(new_question)
        db.session.commit()

    questions = Question.query.filter_by(
        quiz_id=quiz_id
    ).all()

    return render_template(
        'add_question.html',
        quiz=quiz,
        questions=questions,
        message=""
    )


# =========================
# EDIT QUESTION
# =========================
@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):

    question = Question.query.get(id)

    if not question:
        return "Question not found"

    if request.method == 'POST':

        question.question_text = request.form['question']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_answer = request.form['correct_answer']

        db.session.commit()

        return redirect(f'/add_question/{question.quiz_id}')

    return render_template(
        'edit_question.html',
        question=question
    )


# =========================
# DELETE QUESTION
# =========================
@app.route('/delete_question/<int:id>')
def delete_question(id):

    question = Question.query.get(id)

    if not question:
        return "Question not found"

    quiz_id = question.quiz_id

    db.session.delete(question)
    db.session.commit()

    return redirect(f'/add_question/{quiz_id}')


# =========================
# REPORTS
# =========================
@app.route('/reports')
def reports():

    if session.get('role') != 'admin':
        return redirect('/')

    results = db.session.query(
        Result,
        User,
        Quiz
    ).join(
        User,
        Result.student_id == User.id
    ).join(
        Quiz,
        Result.quiz_id == Quiz.id
    ).all()

    return render_template(
        'reports.html',
        results=results
    )


# =========================
# START EXAM
# =========================
@app.route('/start_exam/<int:quiz_id>', methods=['GET', 'POST'])
def start_exam(quiz_id):

    if session.get('role') != 'student':
        return redirect('/')

    quiz = Quiz.query.get(quiz_id)

    questions = Question.query.filter_by(
        quiz_id=quiz_id
    ).all()

    if request.method == 'POST':

        score = 0

        for q in questions:

            ans = request.form.get(str(q.id))

            if ans == q.correct_answer:
                score += 1

        result = Result(
            student_id=session['user_id'],
            quiz_id=quiz_id,
            score=score,
            total=len(questions)
        )

        db.session.add(result)
        db.session.commit()

        return redirect('/view_score')

    return render_template(
        'start_exam.html',
        quiz=quiz,
        questions=questions
    )


# =========================
# VIEW SCORE
# =========================
@app.route('/view_score')
def view_score():

    if session.get('role') != 'student':
        return redirect('/')

    results = Result.query.filter_by(
        student_id=session['user_id']
    ).all()

    attempts_data = db.session.query(
        Result.quiz_id,
        func.count(Result.id)
    ).filter_by(
        student_id=session['user_id']
    ).group_by(
        Result.quiz_id
    ).all()

    attempt_map = {
        a[0]: a[1]
        for a in attempts_data
    }

    return render_template(
        'view_score.html',
        results=results,
        attempt_map=attempt_map
    )


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)