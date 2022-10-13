from db import db


class RecentModel(db.Model):
    __tablename__ = "recent"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, timezone=True)
    content = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel", back_popuplates="users")

    @classmethod
    def get_list(cls):
        return cls.query.order_by(cls.date.desc())

    def save(self):
        rows = self.query.count()

        if rows < 100:
            db.session.add(self)
            db.session.commit()
        else:
            replaced = self.query.order_by(self.date.asc()).first()
            replaced.date = self.date
            replaced.content = self.content
            replaced.user_id = self.user_id
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
