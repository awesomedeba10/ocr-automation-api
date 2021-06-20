from marshmallow import Schema, fields

class UserCreationSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)

class UserProfileSchema(Schema):
    user_id = fields.String(required=True)