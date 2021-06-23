from re import template
from flask import Blueprint, json, request, render_template
import os, sys

from app import app
from app.helper import *
from app.middleware import param_required
from app.modules.templates.schema import *
from app.services.open_cv import CVImage

template_blueprint = Blueprint('template_blueprint', __name__)

@template_blueprint.route('/upload', methods=['POST'])
@param_required(TemplateUploadSchema())
def upload_template():
    file = request.files['template']
    if allowed_file(file.filename):
        user_id = request.form['user_id']
        file_path = os.path.join(app.config.get('STORAGE_DIR'),'users', user_id +'.json')
        if not os.path.isfile(file_path):
            return json.jsonify(format_error({"user_id": ["Invalid User Id"]})), 400

        with open(file_path, 'r') as jsonFile:
            user_info = json.load(jsonFile)
        with open(file_path, 'w') as jsonFile:
            template_id = return_random(length=14)
            file.filename = template_id +'.'+ get_file_extension(file.filename)
            file.save(os.path.join(app.config.get('STORAGE_DIR'), 'templates', file.filename))
            if 'templates' not in user_info:
                user_info['templates'] = {}
            user_info['templates'].update({template_id: {
                'image': file.filename,
                'url': route('template_blueprint.preview_template', user_id=user_id, template_id=template_id),
                'roi': {}
            }})
            json.dump(user_info, jsonFile)
            return json.jsonify({
                'status': True,
                'response': user_info['templates'][template_id]
            })
    else:
        return json.jsonify(format_error({"template": ["File type not supported"]})), 400

@template_blueprint.route('/preview', methods=['GET'])
def preview_template():
    user_id = request.args.get('user_id', '')
    template_id = request.args.get('template_id')
    file_path = os.path.join(app.config.get('STORAGE_DIR'),'users', user_id +'.json')
    if not os.path.isfile(file_path):
        return render_template("preview.html", imgName = 'image-not-found.jpg')
    with open(file_path, 'r') as jsonFile:
        user_info = json.load(jsonFile)
    if template_id not in user_info['templates']:
        return render_template("preview.html", imgName = 'image-not-found.jpg')
    return render_template("preview.html", imgName = 'templates/'+ user_info['templates'][template_id]['image'])

@template_blueprint.route('/add-roi', methods=['POST'])
@param_required(TemplateROISchema())
def add_roi():
    user_id = request.form['user_id']
    file_path = os.path.join(app.config.get('STORAGE_DIR'),'users', user_id +'.json')
    if not os.path.isfile(file_path):
        return json.jsonify(format_error({"user_id": ["Invalid User Id"]})), 400

    with open(file_path, 'r') as jsonFile:
        user_info = json.load(jsonFile)

    template_id = request.form['template_id']
    if template_id not in user_info['templates']:
        return json.jsonify(format_error({"user_id": ["Invalid Template Id"]})), 400

    try:
        roi = eval(request.form['roi'])
    except:
        return json.jsonify(format_error({"roi": ["Invalid Format, failed to retrive ROI"]})), 400
    else:
        user_info['templates'][template_id]['roi'] = roi
        user_info['templates'][template_id]['labeled_url'] = route('template_blueprint.preview_labeled_template',
            user_id=user_id, template_id=template_id),
        with open(file_path, 'w') as jsonFile:
            json.dump(user_info, jsonFile)

    return json.jsonify({
        'status': True,
        'response': 'ROI Added Successfully',
        'template': user_info['templates'][template_id]
    })

@template_blueprint.route('/preview-labeled-template', methods=['GET'])
def preview_labeled_template():
    user_id = request.args.get('user_id', '')
    template_id = request.args.get('template_id')
    file_path = os.path.join(app.config.get('STORAGE_DIR'),'users', user_id +'.json')
    if not os.path.isfile(file_path):
        return render_template("preview.html", imgName = 'image-not-found.jpg')
    with open(file_path, 'r') as jsonFile:
        user_info = json.load(jsonFile)
    if template_id not in user_info['templates']:
        return render_template("preview.html", imgName = 'image-not-found.jpg')
    elif not user_info['templates'][template_id]['roi']:
        return render_template("preview.html", imgName = 'image-not-found.jpg')

    user_template = user_info['templates'][template_id]
    img = CVImage(os.path.join(app.config.get('STORAGE_DIR'), 'templates', user_template['image']))
    for label, roi in user_template['roi'].items():
        img.draw_labeled_frame(roi, label)
    output = user_id + template_id + '.' + get_file_extension(user_template['image'])
    img.write_image(os.path.join(app.config.get('STORAGE_DIR'), 'temp', output))
    return render_template("preview.html", imgName = 'temp/'+ output)