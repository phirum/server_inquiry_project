from models import User, Course, Quiz, Enroll
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, password, role):
    password_hash = generate_password_hash(password)
    user = User(username, password_hash, role)
    user.save()
    return user

def create_course(name):
    course = Course(name)
    course.save()
    return course

def create_quiz(course_id, questions):
    quiz = Quiz(course_id, questions)
    quiz.save()
    return quiz

def enroll_student(course_id, student_id):
    enrollment = Enroll(course_id, student_id)
    enrollment.save()
    return enrollment
