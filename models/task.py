from models.user import db

class Task(db.Model):

    id = db.Column(db.Integer,
                   primary_key=True)

    title = db.Column(db.String(200),
                      nullable=False)

    description = db.Column(db.Text)

    priority = db.Column(db.String(20))

    status = db.Column(db.String(20),
                       default="Pending")

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'))