from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


DEPARTMENTS = [
    ('CSE', 'Computer Science & Engineering'),
    ('ECE', 'Electronics & Communication'),
    ('EEE', 'Electrical & Electronics'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('IT', 'Information Technology'),
    ('GENERAL', 'General / All Departments'),
]


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    department = db.Column(db.String(20), default='GENERAL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses_taught = db.relationship('Course', backref='instructor', lazy='dynamic',
                                     foreign_keys='Course.instructor_id')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic',
                                  cascade='all, delete-orphan')
    attempts = db.relationship('Attempt', backref='student', lazy='dynamic',
                               cascade='all, delete-orphan')
    lesson_progress = db.relationship('LessonProgress', backref='student', lazy='dynamic',
                                      cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_instructor(self):
        return self.role in ('admin', 'instructor')

    def is_student(self):
        return self.role == 'student'

    def can_access_course(self, course):
        if self.is_admin() or self.is_instructor():
            return True
        if not self.is_student():
            return False
        return course.department in (self.department, 'GENERAL')

    def has_passed_quiz(self, quiz_id):
        return Attempt.query.filter_by(
            student_id=self.id, quiz_id=quiz_id, passed=True
        ).first() is not None

    def __repr__(self):
        return f'<User {self.username} ({self.role}/{self.department})>'


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(20), nullable=False, default='GENERAL', index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

    lessons = db.relationship('Lesson', backref='course', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='Lesson.order')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic',
                              cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def enrollment_count(self):
        return self.enrollments.count()

    def __repr__(self):
        return f'<Course {self.title} ({self.department})>'


class Lesson(db.Model):
    """One video lesson inside a course. Pass its quiz to unlock the next lesson."""
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)

    quiz = db.relationship('Quiz', foreign_keys=[quiz_id], post_update=True)
    progress_records = db.relationship('LessonProgress', backref='lesson', lazy='dynamic',
                                       cascade='all, delete-orphan')

    def youtube_embed_id(self):
        if not self.video_url:
            return None
        url = self.video_url.strip()
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        if 'v=' in url:
            return url.split('v=')[-1].split('&')[0]
        if 'embed/' in url:
            return url.split('embed/')[-1].split('?')[0]
        # bare ID
        if len(url) == 11 and ' ' not in url and '/' not in url:
            return url
        return None

    def is_unlocked_for(self, user):
        """First lesson always unlocked. Later lessons need previous lesson quiz passed."""
        if not user or not user.is_authenticated:
            return False
        if user.is_instructor() or user.is_admin():
            return True
        if self.order <= 0:
            return True
        prev = Lesson.query.filter_by(course_id=self.course_id, order=self.order - 1).first()
        if not prev:
            return True
        if not prev.quiz_id:
            # previous had no quiz → consider unlocked if enrolled
            return True
        return user.has_passed_quiz(prev.quiz_id)

    def __repr__(self):
        return f'<Lesson {self.order}: {self.title}>'


class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('student_id', 'lesson_id', name='unique_lesson_progress'),)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    time_limit_minutes = db.Column(db.Integer, default=15)
    passing_score = db.Column(db.Integer, default=60)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

    questions = db.relationship('Question', backref='quiz', lazy='dynamic',
                                cascade='all, delete-orphan', order_by='Question.order')
    attempts = db.relationship('Attempt', backref='quiz', lazy='dynamic',
                               cascade='all, delete-orphan')

    def question_count(self):
        return self.questions.count()


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    order = db.Column(db.Integer, default=0)


class Attempt(db.Model):
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    answers_json = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    passed = db.Column(db.Boolean, default=False)
