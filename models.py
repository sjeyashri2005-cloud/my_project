from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# =========================
# USER TABLE
# =========================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    quizzes = db.relationship('Quiz', backref='teacher', lazy=True)

    # RESULT RELATIONSHIP
    results = db.relationship('Result', backref='student', lazy=True)

    def __repr__(self):
        return f"<User {self.fullname}>"


# =========================
# SUBJECT TABLE
# =========================

class Subject(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)
    chapter_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    quizzes = db.relationship('Quiz', backref='subject', lazy=True)

    def __repr__(self):
        return f"<Subject {self.subject_name}>"


# =========================
# QUIZ TABLE
# =========================

class Quiz(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    # IMPORTANT LINKS (THIS FIX ENABLES SUBJECT WISE FILTER)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    results = db.relationship('Result', backref='quiz', lazy=True)

    __table_args__ = (
        db.UniqueConstraint(
            'title',
            'subject_id',
            'teacher_id',
            name='unique_quiz_rule'
        ),
    )

    def __repr__(self):
        return f"<Quiz {self.title}>"


# =========================
# QUESTION TABLE
# =========================

class Question(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    question_text = db.Column(db.String(300), nullable=False)

    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)

    correct_answer = db.Column(db.String(10), nullable=False)

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    def __repr__(self):
        return f"<Question {self.question_text}>"


# =========================
# RESULT TABLE
# =========================

class Result(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Result Student {self.student_id} Quiz {self.quiz_id}>"