from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS



app = Flask(__name__)

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/quiz_app'
mongo = PyMongo(app)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a more secure key
jwt = JWTManager(app)

# CORS(app, resources={
#     r"/*": {
#     "origins": "http://localhost:3000",
#     "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#     "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#     "supports_credentials": True,  # Allow cookies or credentials
# }})
# Enable CORS with specific settings
cors = CORS(app, resources={
    r"/login": {
        "origins": "http://localhost:3000", 
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
         "supports_credentials": True,  # Allow cookies or credentials
         },
    r"/register": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
        },
    r"/courses": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/users": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/enrollments": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/quizzes": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/take_quiz": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/student_info": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    # Add other routes and origins as needed
})

# Define a collection for each entity
users = mongo.db.users
courses = mongo.db.courses
quizzes = mongo.db.quizzes
enrollments = mongo.db.enrollments

# Utility function to get user role
def get_user_role():
    user = users.find_one({'username': get_jwt_identity()})
    return user.get('role') if user else None

# Register user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    users.insert_one({'username': username, 'password': hashed_password, 'role': role})

    return jsonify({'message': 'User registered successfully'})

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users.find_one({'username': username})

    if not user or not check_password_hash(user.get('password'), password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token})

# Admin - CRUD courses
@app.route('/courses', methods=['POST', 'GET'])
@jwt_required()
def courses_handler():
    role = get_user_role()
    if role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        courses.insert_one(data)
        return jsonify({'message': 'Course created successfully'})

    elif request.method == 'GET':
        all_courses = list(courses.find({}, {'_id': False}))
        return jsonify(all_courses)

# Admin - CRUD users
@app.route('/users', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required()
def users_handler():
    role = get_user_role()
    if role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if users.find_one({'username': username}):
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = generate_password_hash(password)
        users.insert_one({'username': username, 'password': hashed_password, 'role': role})

        return jsonify({'message': 'User created successfully'})

    elif request.method == 'GET':
        all_users = list(users.find({}, {'_id': False}))
        return jsonify(all_users)

    elif request.method == 'PUT':
        data = request.get_json()
        username = data.get('username')
        update_data = data.get('update_data')

        users.update_one({'username': username}, {'$set': update_data})

        return jsonify({'message': 'User updated successfully'})

    elif request.method == 'DELETE':
        username = request.get_json().get('username')
        users.delete_one({'username': username})

        return jsonify({'message': 'User deleted successfully'})

# Admin - CRUD enrollments
@app.route('/enrollments', methods=['POST', 'GET'])
@jwt_required()
def enrollments_handler():
    role = get_user_role()
    if role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        enrollments.insert_one(data)
        return jsonify({'message': 'Enrollment created successfully'})

    elif request.method == 'GET':
        all_enrollments = list(enrollments.find({}, {'_id': False}))
        return jsonify(all_enrollments)

# Teacher - CRUD quizzes
@app.route('/quizzes', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required()
def quizzes_handler():
    role = get_user_role()
    if role != 'teacher':
        return jsonify({'message': 'Access denied'}), 403

    username = get_jwt_identity()

    if request.method == 'POST':
        data = request.get_json()
        quizzes.insert_one(data)
        return jsonify({'message': 'Quiz created successfully'})

    elif request.method == 'GET':
        all_quizzes = list(quizzes.find({'created_by': username}, {'_id': False}))
        return jsonify(all_quizzes)

    elif request.method == 'PUT':
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        update_data = data.get('update_data')

        quizzes.update_one({'_id': quiz_id, 'created_by': username}, {'$set': update_data})

        return jsonify({'message': 'Quiz updated successfully'})

    elif request.method == 'DELETE':
        quiz_id = request.get_json().get('quiz_id')
        quizzes.delete_one({'_id': quiz_id, 'created_by': username})

        return jsonify({'message': 'Quiz deleted successfully'})

# Student - Take quizzes and see results
@app.route('/take_quiz', methods=['POST'])
@jwt_required()
def take_quiz():
    role = get_user_role()
    if role != 'student':
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers')
    
    # Validate quiz and answers
    quiz = quizzes.find_one({'_id': quiz_id})
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404
    
    correct_answers = quiz.get('answers')
    score = 0
    for i, answer in enumerate(answers):
        if answer == correct_answers[i]:
            score += 1
    
    # Store quiz result for the student
    username = get_jwt_identity()
    mongo.db.results.insert_one({
        'username': username,
        'quiz_id': quiz_id,
        'score': score,
    })
    
    return jsonify({'message': 'Quiz taken successfully', 'score': score})

# Student - View courses and results
@app.route('/student_info', methods=['GET'])
@jwt_required()
def student_info():
    role = get_user_role()
    if role != 'student':
        return jsonify({'message': 'Access denied'}), 403

    username = get_jwt_identity()

    # Get courses the student is enrolled in
    enrollments_data = list(enrollments.find({'student_username': username}))
    courses_data = [mongo.db.courses.find_one({'_id': enrollment['course_id']}) for enrollment in enrollments_data]

    # Get quiz results for the student
    results_data = list(mongo.db.results.find({'username': username}))

    return jsonify({
        'courses': courses_data,
        'results': results_data,
    })

if __name__ == '__main__':
    app.run(debug=True)
