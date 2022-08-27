from . import ma
from .models import Ebook, User, UserTypes
from marshmallow_enum import EnumField
class EbookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ebook

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    
    role = EnumField(UserTypes, by_value=True)
