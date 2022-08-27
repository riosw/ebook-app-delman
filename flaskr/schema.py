from . import ma
from .models import Ebook

class EbookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ebook