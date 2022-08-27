from . import ma
from .models import Ebook, Staff

class EbookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ebook

class StaffSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Staff