from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/quiz_app'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change to a secure key
cors=CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# cors = CORS(app, resources={
#     r"/login": {
#         "origins": "http://localhost:3000", 
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#          "supports_credentials": True,  # Allow cookies or credentials
#          },
#     r"/register": {
#         "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#         },
#     r"/courses": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     r"/users": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     r"/enrollments": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     r"/quizzes": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     r"/take_quiz": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     r"/student_info": {
#          "origins": "http://localhost:3000",
#         "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
#         "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
#         "supports_credentials": True,  # Allow cookies or credentials
#     },
#     # Add other routes and origins as needed
# })

# Initialize Flask extensions
mongo = PyMongo(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    mongo.db.users.insert_one({
        'username': username,
        'password': hashed_password,
        'role': role
    })

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')


    user = mongo.db.users.find_one({'username': username})
    print("Hello ");
    print(user['password']);   
    print(password);
    print(check_password_hash(user['password'], password))

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({
        'access_token': access_token,
        'role': user['role']
    })


@app.route('/courses', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def manage_courses():
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    role = user['role']

    if role != 'teacher' and role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        teacher_username = get_jwt_identity()

        mongo.db.courses.insert_one({
            'name': name,
            'description': description,
            'teacher_username': teacher_username
        })

        return jsonify({'message': 'Course created successfully'})

    elif request.method == 'GET':
        courses = list(mongo.db.courses.find({}, {'_id': False}))
        return jsonify(courses)

    elif request.method == 'PUT':
        data = request.get_json()
        course_id = data.get('course_id')
        update_data = data.get('update_data')

        mongo.db.courses.update_one(
            {'_id': course_id},
            {'$set': update_data}
        )

        return jsonify({'message': 'Course updated successfully'})

    elif request.method == 'DELETE':
        data = request.get_json()
        course_id = data.get('course_id')

        mongo.db.courses.delete_one({'_id': course_id})

        return jsonify({'message': 'Course deleted successfully'})



@app.route('/quizzes', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def manage_quizzes():
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    role = user['role']

    if role != 'teacher' and role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        course_id = data.get('course_id')
        questions = data.get('questions')

        mongo.db.quizzes.insert_one({
            'course_id': course_id,
            'questions': questions
        })

        return jsonify({'message': 'Quiz created successfully'})

    elif request.method == 'GET':
        quizzes = list(mongo.db.quizzes.find({}, {'_id': False}))
        return jsonify(quizzes)

    elif request.method == 'PUT':
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        update_data = data.get('update_data')

        mongo.db.quizzes.update_one(
            {'_id': quiz_id},
            {'$set': update_data}
        )

        return jsonify({'message': 'Quiz updated successfully'})

    elif request.method == 'DELETE':
        data = request.get_json()
        quiz_id = data.get('quiz_id')

        mongo.db.quizzes.delete_one({'_id': quiz_id})

        return jsonify({'message': 'Quiz deleted successfully'})


@app.route('/users', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_users():
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    role = user['role']

    if role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if mongo.db.users.find_one({'username': username}):
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password,
            'role': role
        })

        return jsonify({'message': 'User created successfully'})

    elif request.method == 'GET':
        users = list(mongo.db.users.find({}, {'_id': False, 'password': False}))
        return jsonify(users)

    elif request.method == 'PUT':
        data = request.get_json()
        username = data.get('username')
        update_data = data.get('update_data')

        mongo.db.users.update_one(
            {'username': username},
            {'$set': update_data}
        )

        return jsonify({'message': 'User updated successfully'})

    elif request.method == 'DELETE':
        data = request.get_json()
        username = data.get('username')

        mongo.db.users.delete_one({'username': username})

        return jsonify({'message': 'User deleted successfully'})

@app.route('/enrollments', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_enrollments():
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    role = user['role']

    if role != 'admin':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        data = request.get_json()
        course_id = data.get('course_id')
        student_username = data.get('student_username')

        mongo.db.enrollments.insert_one({
            'course_id': course_id,
            'student_username': student_username
        })

        return jsonify({'message': 'Enrollment created successfully'})

    elif request.method == 'GET':
        enrollments = list(mongo.db.enrollments.find({}, {'_id': False}))
        return jsonify(enrollments)

    elif request.method == 'PUT':
        data = request.get_json()
        enrollment_id = data.get('enrollment_id')
        update_data = data.get('update_data')

        mongo.db.enrollments.update_one(
            {'_id': enrollment_id},
            {'$set': update_data}
        )

        return jsonify({'message': 'Enrollment updated successfully'})

    elif request.method == 'DELETE':
        data = request.get_json()
        enrollment_id = data.get('enrollment_id')

        mongo.db.enrollments.delete_one({'_id': enrollment_id})

        return jsonify({'message': 'Enrollment deleted successfully'})

@app.route('/student_info', methods=['GET'])
@jwt_required()
def student_info():
    username = get_jwt_identity()

    student = mongo.db.users.find_one({'username': username})
    if not student or student['role'] != 'student':
        return jsonify({'message': 'Access denied'}), 403

    courses = list(mongo.db.enrollments.find({'student_username': username}, {'_id': False}))
    results = list(mongo.db.results.find({'student_username': username}, {'_id': False}))

    return jsonify({
        'courses': courses,
        'results': results
    })


if __name__ == '__main__':
    app.run(debug=True)