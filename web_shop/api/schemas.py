from marshmallow import Schema, fields, ValidationError, validate
from ..db.data_validators import is_phone_valid


class CategorySchema(Schema):
    id = fields.String()
    title = fields.String(required=True, validate=validate.Length(min=2, max=512))
    slug = fields.String(required=True, validate=validate.Length(min=2, max=512), )
    description = fields.String(validate=validate.Length(max=2048))
    subcategories = fields.List(fields.Nested("self", exclude=['subcategories', 'parent']))
    parent = fields.Nested("self", exclude=['subcategories', 'parent'])


class CustomerSchema(Schema):
    id = fields.String()
    user_id = fields.Integer(required=True)
    username = fields.String(validate=validate.Length(1, 256))
    phone_number = fields.String(validate=is_phone_valid)
    address = fields.String()
    name = fields.String(validate=validate.Length(min=1, max=256))
    surname = fields.String(validate=validate.Length(min=1, max=256))
    age = fields.Integer(validate=validate.Range(1, 99))
    is_blocked = fields.Boolean(default=False)


class CartItemSchema(Schema):
    product = fields.Nested('ProductSchema', required=True)
    count = fields.Integer(default=1, required=True, validate=validate.Range(min=0))


class CartSchema(Schema):
    id = fields.String()
    customer = fields.Nested('CustomerSchema', required=True)
    cart_items = fields.List(fields.Nested('CartItemSchema'))
    is_archived = fields.Boolean(required=True, default=False)


class CharacteristicsSchema(Schema):
    height = fields.Decimal(validate=validate.Range(min=0))
    width = fields.Decimal(validate=validate.Range(min=0))
    weight = fields.Decimal(validate=validate.Range(min=0))


class ProductSchema(Schema):
    id = fields.String()
    title = fields.String(required=True, validate=validate.Length(min=2, max=512))
    slug = fields.String(required=True, validate=validate.Length(min=2, max=512))
    description = fields.String(validate=validate.Length(min=2, max=2048))
    characteristics = fields.Nested("CharacteristicsSchema")
    price = fields.Integer(required=True, validate=validate.Range(min=0))
    discount_percentage = fields.Integer(validate=validate.Range(0, 100), default=0)
    category = fields.Nested('CategorySchema', exclude=['subcategories', 'parent'])
    image = fields.Field(load_only=True)


class NewsSchema(Schema):
    id = fields.String()
    title = fields.String(validate=validate.Length(min=2, max=512))
    body = fields.String(validate=validate.Length(min=10, max=4096))
    pub_date = fields.DateTime()


class TextsSchema(Schema):
    id = fields.String()
    text = fields.String(required=True, validate=validate.Length(min=1, max=256))
    body = fields.String(validate=validate.Length(min=1, max=4096))