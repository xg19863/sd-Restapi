import traceback
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jti
from hmac import compare_digest

from models.user import UserModel  
from models.confirmation import ConfirmationModel
from schemas.user import UserSchema
from libraries.string import gettext
from libraries.mailgun import MailgunException
from blocklist import BLOCKLIST


user_schema = UserSchema()

class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        user = user_schema.load(data)

        if UserModel.find_by_name(user.username):
            return {"msg": gettext("user_exists")}, 400
        if UserModel.find_by_email(user.email):
            return {"msg": gettext("email_used")}, 400

        try:
            user.save()
            confirmation = ConfirmationModel(user.id)
            confirmation.save()
            user.send_email()
            return {"msg": gettext("user_created")}, 201
        except MailgunException as e:
            user.delete()
            return {"msg": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete()
            return {"msg": gettext("failed_creating_user")}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"msg": gettext("user_not_found")}, 404
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required(fresh=True)
    def patch(cls):
        data = request.get_json()
        user = user_schema.load(data)

        user_database = UserModel.find_by_id(user.user_id)
        if not user_database:
            return {"msg": gettext("user_not_found")}, 404
        if not user_database.password and user.email != user_database.email:
            return {"msg": gettext("user_no_password")}, 403
            
        user_database = user
            
        try:
            user_database.save()
        except:
            return {"msg": gettext("failed_updating_user")}, 500
        return {"msg": gettext("user_updated")}, 201


    @classmethod
    @jwt_required(fresh=True)
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if user:
            user.delete()
        return {"msg": gettext("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        user_data = user_schema.load(data, partial=("email",)) 

        user = UserModel.find_by_id(user_data.id)

        if user and compare_digest(user_data.password, user.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"msg": gettext("user_not_confirmed")}

        return {"msg": gettext("invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    def post(cls):
        jti = get_jti()
        BLOCKLIST.add(jti)
        return {"msg": gettext("user_logout")}, 200


class UserMessages(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"msg": gettext("user_not_found")}, 404

        return jsonify(user.messages)


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(fresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
