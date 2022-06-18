from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()
 
class EventModel(db.Model):
    __tablename__ = "table"
 
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer(),unique = True)
    heading = db.Column(db.String())
    date = db.Column(db.string())
    time = db.Column(db.string())
    tag =db.Column(db.string(10)) #tag=academic , sports , club  
    description=db.Column(db.string()) #regarding scores , winners ,etc

    def __init__(self, event_id,heading,date,time,tag,description):
        self.event_id = event_id
        self.heading = heading
        self.date = date 
        self.time = time
        self.tag = tag
        self.description= description
 
    def __repr__(self):
        return f"{self.heading}:{self.date}:{self.time}:{self.tag}"

