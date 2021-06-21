from flask import Flask
from flask.helpers import send_from_directory

app = Flask(__name__, template_folder='html')
app.url_map.strict_slashes = False
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return {'response': str(error)}, 404

@app.errorhandler(405)
def not_found(error):
    return {'response': str(error)}, 405

@app.route('/preview/<path:imgName>')
def preview_file(imgName):
    return send_from_directory(app.config.get('STORAGE_DIR'), imgName)

# ! Importing blueprints here...
from app.modules.users.controller import user_blueprint
from app.modules.templates.controller import template_blueprint


app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(template_blueprint, url_prefix="/template")