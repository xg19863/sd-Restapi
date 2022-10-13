import os
import traceback
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libraries import image_helper
from libraries.string import gettext
from schemas.image import ImageSchema


image_schema = ImageSchema()

class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder= f"user_{user_id}"

        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"msg": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            ext = image_helper.get_extension(data["image"])
            return {"msg": gettext("image_format_not_allowed").format(ext)}, 400

class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_extension_safe(filename):
            return {"msg": gettext("image_name_not_allowed").format(filename)}, 400

        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"msg": gettext("image_not_found")}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_extension_safe(filename):
            return {"msg": gettext("image_name_not_allowed").format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"msg": gettext("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"msg": gettext("image_not_found")}, 404
        except:
            traceback.print_exc()
            return {"msg": gettext("image_deletion_failed")}, 500


class AvatarUpload(Resource):
    @jwt_required
    def put(self):
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"msg": gettext("avatar_deletion_failed")}, 500

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path  =image_helper.save_image(data["image"], folder=folder, name=avatar)
            return {"msg": gettext("avatar_uploaded")}, 200
        except UploadNotAllowed:
            ext = image_helper.get_extension(data["image"])
            return {"msg": gettext("image_type_not_allowed").format(ext)}, 400


class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"msg": gettext("avatar_not_found")}, 404
