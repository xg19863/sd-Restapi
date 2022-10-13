import json
from flask import url_for
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from uuid import uuid4

from oa import oauth
from models.user import UserModel
from libraries.string import gettext


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        return oauth.github.authorize(url_for("github.authorize", _external=True))


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        token =oauth.github.authorize_access_token()

        if token is None:
            error_response = {
                "error": gettext("oauth_token_missing"),
                "error_description": gettext("oauth_token_missing")
            }
            return error_response

        github_user = oauth.github.get("user")
        profile = json.loads(github_user.text)
        github_email = profile["email"]
        
        user = UserModel.find_by_email(github_email)

        if not user:
            user = UserModel(username=f"user_{uuid4()}", password=None, email=github_email)
            if UserModel.find_by_name(user.username):
                while UserModel.find_by_name(user.username):
                    user.username = f"user_{uuid4()}"
            user.save()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}, 200
