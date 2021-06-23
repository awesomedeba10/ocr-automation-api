from marshmallow import Schema, fields

class LabelPreviewSchema(Schema):
    user_id = fields.String(required=True)
    template_id = fields.String(required=True)

