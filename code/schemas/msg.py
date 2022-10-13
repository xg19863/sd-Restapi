from ma import ma
from models.msg import MessageModel


class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MessageModel
        load_instance = True
        dump_only = ("date","content")
        include_fk = True
