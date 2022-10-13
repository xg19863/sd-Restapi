from ma import ma
from models.recent import RecentModel


class RecentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecentModel
        load_instance = True
        dump_only = ("date","content")
        include_fk = True
