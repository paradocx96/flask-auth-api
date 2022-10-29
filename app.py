import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pymongo import MongoClient

# Flask Configuration
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
load_dotenv()

# MongoDB Configuration
# Import Connection String from env
try:
    mongodb_url_with_db = os.getenv('mongodb_url_with_db')
    mongodb_url_without_db = os.getenv('mongodb_url_without_db')
except BaseException:
    mongodb_url_with_db = os.environ['mongodb_url_with_db']
    mongodb_url_without_db = os.environ['mongodb_url_without_db']

# Configurate DB URL to Flask App
app.config["MONGO_URI"] = mongodb_url_with_db
mongo = PyMongo(app)

# Create mongo client
myClient = MongoClient(mongodb_url_without_db)
db = myClient["de_db"]

"""
Root Endpoints

@hello_world()
/ [GET] - Hello World
"""


@app.route('/')
def hello_world():
    return 'Hello World!'


"""
Auth Endpoints

@auth_signin()
/auth/signin [POST] - User SignIn

@auth_signup()
/auth/signup [POST] - User SignUp
"""


# User SignIn method
@app.route('/auth/signin', methods=['POST'])
def auth_signin():
    # Get JSON data
    _json = request.json
    _username = _json['username']
    _password = _json['password']

    # validate the received values
    if _username and _password and request.method == 'POST':
        # Check username availability in database
        check_user = mongo.db.user.find_one({"username": _username})

        # Check user is available or not
        if check_user is None:
            # Send response for username availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Incorrect!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Check password is match with user given
            if check_user['password'] != _password:
                # Send response for password incorrect
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'Password Incorrect!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            # Checking password correction
            elif check_user['password'] == _password:
                # Create JSON response data
                res = {
                    "full_name": check_user['full_name'],
                    "username": check_user['username'],
                    "email": check_user['email'],
                    "role": check_user['role'],
                    "image": check_user['image'],
                    'created': check_user['created'],
                    'updated': check_user['updated']
                }

                # Send response for user signin
                response = jsonify({
                    "code": 200,
                    "message": "Success",
                    "data": res
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Send response for error
                response = jsonify({
                    "code": 204,
                    "message": "Unsuccessful",
                    "data": 'Something Wrong!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 204
    else:
        # Send response for error
        return not_found()


# User SignUp method
@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    # Get JSON data
    _json = request.json
    _fullName = _json['full_name']
    _username = _json['username']
    _email = _json['email']
    _password = _json['password']
    _role = _json['role']
    _image = _json['image']

    # Getting current data time
    current_date_time = datetime.now()
    _created = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _fullName and _username and _email and _password and _role and request.method == 'POST':
        # Check username availability in database
        check_username = mongo.db.user.find_one({"username": _username})

        # Check email availability in database
        check_email = mongo.db.user.find_one({"email": _email})

        # Check username availability
        if check_username is not None:
            # Send response for username availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200

        # Check user availability
        elif check_email is not None:
            # Send response for email availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Email Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Creating new user
            res = mongo.db.user.insert_one({
                'full_name': _fullName,
                'username': _username,
                'email': _email,
                'password': _password,
                'role': _role,
                'image': _image,
                'created': _created,
                'updated': "default"
            })

            # Send response for user registration
            response = jsonify({
                "code": 201,
                "message": "Success",
                "data": 'User Registration Successfully!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 201
    else:
        # Send response for error
        return not_found()


"""
User Management Endpoints

@get_all_users()
/user [GET] - Get all users

@get_user_by_id(uid)
/user/<id> [GET] - Get user by Id

@delete_user(uid)
/user/<id> [DELETE] - Delete user by Id

@update_user()
/user [PUT] - Update user

@update_password()
/user/change/password [PUT] - Update password

@update_username()
/user/change/username [PUT] - Update username
"""


# User - Get All method
@app.route('/user')
def get_all_users():
    # Get all available users
    user = mongo.db.user.find()

    # Convert data to JSON data
    resp = dumps(user, indent=2)
    return resp


# User - Get By Id method
@app.route('/user/<uid>')
def get_user_by_id(uid):
    try:
        # Find user by user id
        user = mongo.db.user.find_one({'_id': ObjectId(uid)})

        # Check user availability
        if user is None:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Create JSON data
            data = {
                "_id": uid,
                "full_name": user['full_name'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "image": user['image'],
                'created': user['created'],
                'updated': user['updated']
            }

            # Send response for available user
            response = jsonify({
                "code": 200,
                "message": "Success",
                "data": data
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    except:
        # Send response for dose not exists
        response = jsonify({
            "code": 200,
            "message": "Unsuccessful",
            "data": 'User Does Not Exists!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200


# User - Delete by Id method
@app.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    # validate the received values
    if uid and request.method == 'DELETE':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(uid)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Delete user form database
                res = mongo.db.user.delete_one({'_id': ObjectId(uid)})

                # Send response for user remove
                response = jsonify({
                    "code": 202,
                    "message": "Success",
                    "data": 'User Delete Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 202
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update method
@app.route('/user', methods=['PUT'])
def update_user():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _fullName = _json['full_name']
    _email = _json['email']
    _role = _json['role']
    _image = _json['image']

    # Getting current data time
    current_date_time = datetime.now()
    _updated = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _fullName and _email and _role and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # save update updated user data in database
                res = mongo.db.user.update_one(
                    {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                    {'$set': {
                        'full_name': _fullName,
                        'email': _email,
                        'role': _role,
                        'image': _image,
                        'updated': _updated
                    }}
                )

                # Send response for user update successful
                response = jsonify({
                    "code": 201,
                    "message": "Success",
                    "data": 'User Update Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update Password method
@app.route('/user/change/password', methods=['PUT'])
def update_password():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _password = _json['password']

    # Getting current data time
    date_time_password = datetime.now()
    _updated_password_time = date_time_password.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _password and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            # Check user available
            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # save new password in database
                res = mongo.db.user.update_one(
                    {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                    {'$set': {
                        'password': _password,
                        'updated': _updated_password_time
                    }}
                )

                # Send response for update password in database
                response = jsonify({
                    "code": 201,
                    "message": "Success",
                    "data": 'Password Update Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update Username method
@app.route('/user/change/username', methods=['PUT'])
def update_username():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _username = _json['username']

    # Getting current data time
    date_time_username = datetime.now()
    _updated_username_time = date_time_username.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _username and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Find user by username
                check_username = mongo.db.user.find_one({"username": _username})

                # Check user available
                if check_username is not None:
                    # Send response for username availability
                    response = jsonify({
                        "code": 200,
                        "message": "Unsuccessful",
                        "data": 'Username Already Exists!'
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 200
                else:
                    # save new password in database
                    res = mongo.db.user.update_one(
                        {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                        {'$set': {
                            'username': _username,
                            'updated': _updated_username_time
                        }}
                    )

                    # Send response for username update success
                    response = jsonify({
                        "code": 201,
                        "message": "Success",
                        "data": 'Username Update Successfully!'
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# Endpoint Error Response
@app.errorhandler(404)
def not_found(error=None):
    # Send response for Endpoint error
    response = jsonify({
        "code": 404,
        "message": "Unsuccessful",
        "url": 'Not Found: ' + request.url
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404


if __name__ == '__main__':
    app.run()
