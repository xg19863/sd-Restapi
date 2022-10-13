from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from models.msg import MessageModel
from models.recent import RecentModel
from schemas.msg import MessageSchema
from schemas.recent import RecentSchema
from libraries.string import gettext


message_schema = MessageSchema()
recent_schema = RecentSchema()

class Message(Resource):
    @classmethod
    def get(cls, msg_id: int):
        msg = MessageModel.get_single(msg_id)

        if not msg:
            return {"msg": gettext("message_not_found")}, 404
        return message_schema.dump(msg), 200

    @classmethod
    @jwt_required
    def post(cls):
        data = request.get_json()
        msg = message_schema.load(data)
        recent = recent_schema.load(data)

        try:
            msg.save()
        except:
            return {"msg": gettext("failed_saving_msg")}, 500

        recent.save()
        return {"msg": gettext("message_sent")}, 201

    @classmethod
    @jwt_required
    def delete(cls, msg_id: int):
        msg = MessageModel.get_single(msg_id)

        if msg:
            msg.delete()
        return {"msg": gettext("message_deleted")}, 200


class Recent(Resource):
    @classmethod
    def get(cls):
        return RecentModel.get_list()
