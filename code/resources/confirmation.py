from time import time
import traceback
from flask import make_response, render_template
from flask_restful import Resource

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from libraries.mailgun import MailgunException
from libraries.string import gettext


confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"msg": gettext("confirmation_not_found")}, 404

        if confirmation.expired:
            return {"msg": gettext("confirmation_expired")}, 400

        if confirmation.confirmed:
            return {"msg": gettext("confirmation_already_used")}, 400

        confirmation.confirmed = True
        confirmation.save()
        
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirm.html", email=confirmation.user.email), 200, headers)


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"msg": gettext("user_not_found")}, 404

        return ({
            "current_time": int(time()),
            "confirmation": [
                confirmation_schema.dump(row) for row in user.confirmation.order_by(ConfirmationModel.expire_at)
            ]
        }, 200)

    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"msg": gettext("user_not_found")}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"msg": "confirmation_already_used"}, 400
                confirmation.force_expire()
            
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save()
            user.send_email()
            return {"msg": "resend_success"}, 201
        except MailgunException as e:
            return {"msg": str(e)}, 500
        except:
            traceback.print_exc()
            return {"msg": "resend_failed"}, 500
