from flask import Flask

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return {'response': str(error)}, 404

@app.errorhandler(405)
def not_found(error):
    return {'response': str(error)}, 405

# ! Importing blueprints here...
from app.modules.users.controller import user_blueprint


app.register_blueprint(user_blueprint, url_prefix="/user")