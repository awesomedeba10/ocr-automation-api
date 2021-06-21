from marshmallow import Schema, fields

class TemplateUploadSchema(Schema):
    user_id = fields.String(required=True)