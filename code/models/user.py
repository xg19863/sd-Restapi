from flask import request, url_for

from db import db
from libraries.mailgun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(40))
    email = db.Column(db.string(80), nullable=False, unique=True)

    messages = db.relationship("MessageModel", cascade="all, delete-orphan", lazy="dynamic")
    recent = db.relationship("RecentModel", cascade="all, delete-orphan", lazy="dynamic")
    confirmation = db.relationship("ConfirmationModel", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def most_recent_confirmation(self):
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_name(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    def send_email(self):
        link = request.url_root[:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation)
        subject = "Confirmation Email"
        text = f"Please click on the link to finish your registeration: {link}"
        html = f"<html>Please click on the link to finish your registeration: <a href={link}>link</a></html>"

        return Mailgun.send_email([self.email], subject, text, html)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
