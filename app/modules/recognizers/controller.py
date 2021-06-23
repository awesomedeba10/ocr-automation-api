from flask import Blueprint, json, request, render_template
import os, sys

from app import app
from app.helper import *
from app.middleware import param_required
from app.modules.recognizers.schema import *
from app.services.open_cv import CVImage

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


        print(matchedImg)
        # for label, roi in user_template['roi'].items():
        #     img.draw_labeled_frame(roi, label)
        # output = user_id + template_id + '.' + get_file_extension(user_template['image'])
        # img.write_image(os.path.join(app.config.get('STORAGE_DIR'), 'temp', output))
        # return render_template("preview.html", imgName = 'temp/'+ output)
        return 'hii'
    else:
        return json.jsonify(format_error({"user_doc": ["File type not supported"]})), 400