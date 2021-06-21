from re import template
from flask import Blueprint, json, request
import os

from app import app
from app.helper import *
from app.middleware import login_required, param_required
from app.modules.users.schema import *

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/create', methods=['POST'])
@param_required(UserCreationSchema())
def create():
    user_info = dict(request.form)
    user_info['user_id'] = return_random()
    user_info['templates'] = {}

    with open(os.path.join(app.config.get('STORAGE_DIR'),'users', user_info['user_id']+'.json'), 'w') as jsonFile:
        json.dump(user_info, jsonFile)

    return json.jsonify({
        'status': True,
        'message': 'User ID Created Successfully',
        'response': {
            'user_id': user_info['user_id']
        }
    })

@user_blueprint.route('/profile', methods=['POST'])
@param_required(UserProfileSchema())
def profile():
    user_id = request.form['user_id']
    try:
        with open(os.path.join(app.config.get('STORAGE_DIR'),'users', user_id +'.json'), 'r') as jsonFile:
            return json.jsonify({
                'status': True,
                'response': json.load(jsonFile)
            })
    except FileNotFoundError:
        return json.jsonify(format_error({"user_id": ["Invalid User Id"]})), 400
