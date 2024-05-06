from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Connect to your MongoDB server
db = client.quiz_app  # Connect to your database

# JWT setup
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
jwt = JWTManager(app)

# Models
class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password  # Store password securely (hash it!)
        self.role = role  # 'teacher', 'student', 'admin'

class Course:
    def __init__(self, name, teacher_id):
        self.name = name
        self.teacher_id = teacher_id

class Quiz:
    def __init__(self, course_id, questions):
        self.course_id = course_id
        self.questions = questions  # List of questions with options and answers

# Endpoints

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if db.users.find_one({'username': username}):
        return jsonify({'error': 'User already exists'}), 400
    
    db.users.insert_one({
        'username': username,
        'password': password,  # You should hash the password
        'role': role
    })
    return jsonify({'message': 'User registered successfully'}), 201

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = db.users.find_one({'username': username, 'password': password})
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity={'username': username, 'role': user['role']})
    return jsonify({'access_token': access_token}), 200

# Create a course (only teachers and admins)
@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    identity = get_jwt_identity()
    role = identity.get('role')
    
    if role not in ['teacher', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    name = data.get('name')
    teacher_id = data.get('teacher_id')
    
    course_id = db.courses.insert_one({
        'name': name,
        'teacher_id': teacher_id
    }).inserted_id
    
    return jsonify({'course_id': str(course_id)}), 201

# Create a quiz (only teachers and admins)
@app.route('/quizzes', methods=['POST'])
@jwt_required()
def create_quiz():
    identity = get_jwt_identity()
    role = identity.get('role')
    
    if role not in ['teacher', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    course_id = data.get('course_id')
    questions = data.get('questions')
    
    quiz_id = db.quizzes.insert_one({
        'course_id': course_id,
        'questions': questions
    }).inserted_id
    
    return jsonify({'quiz_id': str(quiz_id)}), 201

# Get courses
@app.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = list(db.courses.find({}, {'_id': 0}))
    return jsonify(courses), 200

# Get quizzes for a course
@app.route('/courses/<course_id>/quizzes', methods=['GET'])
@jwt_required()
def get_course_quizzes(course_id):
    quizzes = list(db.quizzes.find({'course_id': ObjectId(course_id)}, {'_id': 0}))
    return jsonify(quizzes), 200

# Take a quiz
@app.route('/quizzes/<quiz_id>/take', methods=['POST'])
@jwt_required()
def take_quiz(quiz_id):
    data = request.json
    user_id = get_jwt_identity()['username']
    answers = data.get('answers')
    
    quiz = db.quizzes.find_one({'_id': ObjectId(quiz_id)})
    
    # Calculate score
    score = 0
    for question, answer in zip(quiz['questions'], answers):
        if question['answer'] == answer:
            score += 1
    
    # Save the result
    db.results.insert_one({
        'quiz_id': quiz_id,
        'user_id': user_id,
        'score': score,
        'date_taken': datetime.datetime.utcnow()
    })
    
    return jsonify({'score': score}), 200

if __name__ == '__main__':
    app.run(port=5000)
