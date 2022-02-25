from flask import Blueprint, json, request, render_template
import os, sys

from app import app
from app.helper import *
from app.middleware import param_required
from app.modules.recognizers.schema import *
from app.services.open_cv import CVImage
from app.services.text_extractor import TextExtractor

recognizer_blueprint = Blueprint('recognizer_blueprint', __name__)

@recognizer_blueprint.route('/show-labeled-area', methods=['POST'])
@param_required(LabelPreviewSchema())
def preview_labeled_template():
    user_doc = request.files['user_doc']
    if allowed_file(user_doc.filename):
        user_id = request.form['user_id']
        template_id = request.form['template_id']
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
        user_doc.filename = template_id +'_'+ user_doc.filename
        user_doc.save(os.path.join(app.config.get('STORAGE_DIR'), 'temp', user_doc.filename))

        templateObj = CVImage(os.path.join(app.config.get('STORAGE_DIR'), 'templates', user_template['image']))
        matchedImg = templateObj.initdocument(os.path.join(app.config.get('STORAGE_DIR'), 'temp',
            user_doc.filename)).match_keypoints()
        labeledDoc = templateObj.drawLabelsonDoc(matchedImg, user_template['roi'], alpha=0.45)
        templateObj.write_targeted_image(os.path.join(app.config.get('STORAGE_DIR'), 'temp', user_doc.filename),
            image=labeledDoc)
        return json.jsonify({
            'status': True,
            'preview_url': route('template_blueprint.preview_labeled_document', user_id=user_id,
                template_id=template_id, output_file='temp/'+ user_doc.filename)
        })
    else:
        return json.jsonify(format_error({"user_doc": ["File type not supported"]})), 400

@recognizer_blueprint.route('/recognize-text', methods=['POST'])
@param_required(LabelPreviewSchema())
def detect_text():
    user_docs = request.files.getlist('user_doc')
    prediction_lists = []
    for user_doc in user_docs:
        if allowed_file(user_doc.filename):
            user_id = request.form['user_id']
            template_id = request.form['template_id']
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
            user_doc.filename = template_id +'_'+ user_doc.filename
            user_doc.save(os.path.join(app.config.get('STORAGE_DIR'), 'temp', user_doc.filename))

            templateObj = CVImage(os.path.join(app.config.get('STORAGE_DIR'), 'templates', user_template['image']))
            matchedImg = templateObj.initdocument(os.path.join(app.config.get('STORAGE_DIR'), 'temp',
                user_doc.filename)).match_keypoints()
            cropped_images = templateObj.getCroppedImage(matchedImg, user_template['roi'])

            # preprocessed_img1 = templateObj.adaptative_thresholding(cropped_images)
            # preprocessed_img2 = templateObj.noise_removal(preprocessed_img1)
            # preprocessed_img3 = templateObj.thick_font(preprocessed_img2)

            recognizer = TextExtractor()
            predictions = recognizer.build_data(cropped_images, return_string = True)
            print(predictions)
            prediction_lists.append(predictions)
        else:
            return json.jsonify(format_error({"user_doc": ["One or more files type not supported"]})), 400

    return json.jsonify({
        'status': True,
        'predicted': prediction_lists
    })
