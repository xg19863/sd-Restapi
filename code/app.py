from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError
from dotenv import load_dotenv

load_dotenv(".env", verbose=True)

from db import db
from ma import ma
from oa import oauth
from blocklist import BLOCKLIST
from resources.user import User, UserLogin, UserLogout, UserRegister, UserMessages
from resources.msg import Message, Recent
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import Image, ImageUpload, Avatar, AvatarUpload
from resources.github_login import GithubLogin, GithubAuthorize
from libraries.image_helper import IMAGE_SET


app = Flask(__name__)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, 20 * 1024 * 1024) # 20 MB max size of 1024*1024
configure_uploads(app, IMAGE_SET)
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(e):
    return jsonify(e.messages), 400

@jwt.token_in_blocklist_loader
def check_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


api.add_resource(Recent, "/home")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserRegister, "/register>")
api.add_resource(UserLogin, "/login>")
api.add_resource(UserLogout, "/logout>")
api.add_resource(UserMessages, "/msg/<int:user_id>>")
api.add_resource(Message, "/msg/<int:msg_id>")
api.add_resource(Confirmation, "/confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirm/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorize", endpoint="github.authorize")


if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000)
