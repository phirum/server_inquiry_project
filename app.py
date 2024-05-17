from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/quiz_app'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change to a secure key
# cors=CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


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
    r"/courses/*": {
         "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True,  # Allow cookies or credentials
    },
    r"/users/*": {
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
    r"/quizzes/*": {
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


# @app.route('/courses', methods=['GET', 'POST', 'PUT', 'DELETE'])
# @jwt_required()
# def manage_courses():
#     user = mongo.db.users.find_one({'username': get_jwt_identity()})
#     role = user['role']

#     if role != 'teacher' and role != 'admin':
#         return jsonify({'message': 'Access denied'}), 403

#     if request.method == 'POST':
#         data = request.get_json()
#         name = data.get('name')
#         description = data.get('description')
#         teacher_username = get_jwt_identity()

#         mongo.db.courses.insert_one({
#             'name': name,
#             'description': description,
#             'teacher_username': teacher_username
#         })

#         return jsonify({'message': 'Course created successfully'})

#     elif request.method == 'GET':
#         courses = list(mongo.db.courses.find({}, {'_id': False}))
#         return jsonify(courses)

#     elif request.method == 'PUT':
#         data = request.get_json()
#         course_id = data.get('course_id')
#         update_data = data.get('update_data')

#         mongo.db.courses.update_one(
#             {'_id': course_id},
#             {'$set': update_data}
#         )

#         return jsonify({'message': 'Course updated successfully'})

#     elif request.method == 'DELETE':
#         data = request.get_json()
#         course_id = data.get('course_id')

#         mongo.db.courses.delete_one({'_id': course_id})

#         return jsonify({'message': 'Course deleted successfully'})

# CRUD operations for courses

@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    """Create a new course."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['teacher', 'admin']:
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    new_course = {
        'name': name,
        'description': description,
        'teacher_username': user['username']
    }

    course_id = mongo.db.courses.insert_one(new_course).inserted_id
    new_course['_id'] = str(course_id)

    return jsonify(new_course), 201

@app.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():

    """Get a list of courses with pagination."""
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', 20))
  

    courses_cursor = mongo.db.courses.find().skip(page * page_size).limit(page_size)
    courses = list(courses_cursor)
    
    total_courses = mongo.db.courses.count_documents({})

    # Convert ObjectId to str for JSON serialization
    for course in courses:
        course['_id'] = str(course['_id'])

    
   
    return jsonify({
        'data': courses,
        'total': total_courses
    })

@app.route('/courses/<course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """Update a course by its ID."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['teacher', 'admin']:
        return jsonify({'message': 'Access denied'}), 403
    print("Updating Course");
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    updated_course = {
        'name': name,
        'description': description
    }
    print(updated_course);
    print(course_id);
    course_id = ObjectId(course_id);
    print(course_id);
    result = mongo.db.courses.update_one(
        {'_id': course_id},
        {'$set': updated_course}
    )
    print(result);

    if result.matched_count == 0:
        return jsonify({'message': 'Course not found'}), 404

    # Retrieve the updated course
    course = mongo.db.courses.find_one({'_id': course_id})
    course['_id'] = str(course['_id'])

    print(course);
    return jsonify(course), 200

@app.route('/courses/<course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """Delete a course by its ID."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['teacher', 'admin']:
        return jsonify({'message': 'Access denied'}), 403
    course_id = ObjectId(course_id);
    result = mongo.db.courses.delete_one({'_id': course_id})

    if result.deleted_count == 0:
        return jsonify({'message': 'Course not found'}), 404

    return jsonify({'message': 'Course deleted successfully'}), 200



# @app.route('/quizzes', methods=['GET', 'POST', 'PUT', 'DELETE'])
# @jwt_required()
# def manage_quizzes():
#     user = mongo.db.users.find_one({'username': get_jwt_identity()})
#     role = user['role']

#     if role != 'teacher' and role != 'admin':
#         return jsonify({'message': 'Access denied'}), 403

#     if request.method == 'POST':
#         data = request.get_json()
#         course_id = data.get('course_id')
#         questions = data.get('questions')

#         mongo.db.quizzes.insert_one({
#             'course_id': course_id,
#             'questions': questions
#         })

#         return jsonify({'message': 'Quiz created successfully'})

#     elif request.method == 'GET':
#         quizzes = list(mongo.db.quizzes.find({}, {'_id': False}))
#         return jsonify(quizzes)

#     elif request.method == 'PUT':
#         data = request.get_json()
#         quiz_id = data.get('quiz_id')
#         update_data = data.get('update_data')

#         mongo.db.quizzes.update_one(
#             {'_id': quiz_id},
#             {'$set': update_data}
#         )

#         return jsonify({'message': 'Quiz updated successfully'})

#     elif request.method == 'DELETE':
#         data = request.get_json()
#         quiz_id = data.get('quiz_id')

#         mongo.db.quizzes.delete_one({'_id': quiz_id})

#         return jsonify({'message': 'Quiz deleted successfully'})

# Create a quiz
@app.route('/quizzes', methods=['POST'])
def create_quiz():
    print("start of create_quiz");
    data = request.json
    print(data);
    new_quiz = {
        'quizName': data['quizName'],
        'course_id': data['course_id'],
        'questions': data['questions']
    }
    result = mongo.db.quizzes.insert_one(new_quiz)
    new_quiz['_id'] = str(result.inserted_id)
    return jsonify(new_quiz)

# Get all quizzes
@app.route('/quizzes', methods=['GET'])
def get_quizzes():
    quizzes_cursor = mongo.db.quizzes.find()
    quizzes = list(quizzes_cursor)
    
    for quizze in quizzes:
        quizze['_id'] = str(quizze['_id'])
    
    return jsonify(quizzes)

@app.route("/quizzes/<quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    print("geting by Id")
    print(quiz_id);
    try:
        quiz = mongo.db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        if quiz:
            quiz['_id'] = str( quiz['_id'])
            print(quiz)
            return jsonify(quiz), 200
        else:
            return jsonify({"message": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Update a quiz
@app.route('/quizzes/<quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    data = request.json
    mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {'$set': data})
    return jsonify({'message': 'Quiz updated successfully'})

# Delete a quiz
@app.route('/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    mongo.db.quizzes.delete_one({'_id': ObjectId(quiz_id)})
    return jsonify({'message': 'Quiz deleted successfully'})

# API endpoint for submitting a quiz
@app.route("/quizzes/<quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    try:
        # Get quiz data from request
        quiz_data = request.json
        
        # Calculate score (for simplicity, assuming correct answer index is provided)
        quiz = mongo.db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        correct_answers = [q['correctAnswer'] for q in quiz['questions']]
        submitted_answers = quiz_data['answers']
        score = sum(1 for i in range(len(correct_answers)) if correct_answers[i] == submitted_answers[i])

        # Save quiz result to database
        result = {
            "student_id": quiz_data["student_id"],
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": len(correct_answers)
        }
        mongo.db.quiz_results.insert_one(result)

        return jsonify({"message": "Quiz submitted successfully", "score": score}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500



# @app.route('/users', methods=['POST', 'GET', 'PUT', 'DELETE'])
# @jwt_required()
# def manage_users():
#     user = mongo.db.users.find_one({'username': get_jwt_identity()})
#     role = user['role']

#     if role != 'admin':
#         return jsonify({'message': 'Access denied'}), 403

#     if request.method == 'POST':
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')
#         role = data.get('role')

#         if mongo.db.users.find_one({'username': username}):
#             return jsonify({'message': 'User already exists'}), 400

#         hashed_password = generate_password_hash(password)
#         mongo.db.users.insert_one({
#             'username': username,
#             'password': hashed_password,
#             'role': role
#         })

#         return jsonify({'message': 'User created successfully'})

#     elif request.method == 'GET':
#         users = list(mongo.db.users.find({}, {'_id': False, 'password': False}))
#         return jsonify(users)

#     elif request.method == 'PUT':
#         data = request.get_json()
#         username = data.get('username')
#         update_data = data.get('update_data')

#         mongo.db.users.update_one(
#             {'username': username},
#             {'$set': update_data}
#         )

#         return jsonify({'message': 'User updated successfully'})

#     elif request.method == 'DELETE':
#         data = request.get_json()
#         username = data.get('username')

#         mongo.db.users.delete_one({'username': username})

#         return jsonify({'message': 'User deleted successfully'})
@app.route('/users', methods=['POST'])
@jwt_required()
def create_users():
    """Create a new User."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['admin']:
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)

    new_user = {
        'username': username,
        'password': hashed_password,
        'role': role
    }
    user_id = mongo.db.users.insert_one(new_user).inserted_id
    new_user['_id'] = str(user_id)

    return jsonify(new_user), 201

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():

    """Get a list of users with pagination."""
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', 20))
  

    users_cursor = mongo.db.users.find().skip(page * page_size).limit(page_size)
    users = list(users_cursor)
    
    total_users = mongo.db.users.count_documents({})

    # Convert ObjectId to str for JSON serialization
    for user in users:
        user['_id'] = str(user['_id'])

    
   
    return jsonify({
        'data': users,
        'total': total_users
    })

@app.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_users(user_id):
    """Update a course by its ID."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['admin']:
        return jsonify({'message': 'Access denied'}), 403
    print("Updating user");

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400
    print(password)
    hashed_password = generate_password_hash(password)

    updated_user = {
        'username': username,
        'password': hashed_password,
        'role': role
    }
    user_id = ObjectId(user_id);
    result = mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': updated_user}
    )

    if result.matched_count == 0:
        return jsonify({'message': 'Course not found'}), 404

    # Retrieve the updated course
    user = mongo.db.users.find_one({'_id': user_id})
    user['_id'] = str(user['_id'])

    print(user);
    return jsonify(user), 200

@app.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user by its ID."""
    user = mongo.db.users.find_one({'username': get_jwt_identity()})
    if not user or user['role'] not in ['admin']:
        return jsonify({'message': 'Access denied'}), 403
    user_id = ObjectId(user_id);
    result = mongo.db.users.delete_one({'_id': user_id})

    if result.deleted_count == 0:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User deleted successfully'}), 200

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