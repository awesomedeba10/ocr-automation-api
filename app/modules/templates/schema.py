from marshmallow import Schema, fields

class TemplateUploadSchema(Schema):
    user_id = fields.String(required=True)

class TemplateROISchema(Schema):
    user_id = fields.String(required=True)
    template_id = fields.String(required=True)
    roi = fields.Raw(required=True)