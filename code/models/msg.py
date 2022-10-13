from db import db


class MessageModel(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, timezone=True)
    content = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel", back_populates="messages")

    @classmethod
    def get_single(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_recent(cls):
        return cls.query.order_by(cls.date.desc())
    
    @classmethod
    def get_by_user(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id).order_by(cls.date.desc())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
