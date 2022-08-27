from . import ma
from .models import Ebook, User, Order, UserTypes
from marshmallow_enum import EnumField
from marshmallow import fields


class EbookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ebook


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    
    role = EnumField(UserTypes, by_value=True)


class OrderSchema(ma.SQLAlchemySchema):
    ebook = fields.Nested(EbookSchema)
    class Meta:
        fields = ('ebook', 'harga', 'order_date')
        ordered = True
