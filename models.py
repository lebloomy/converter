from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator, VARCHAR
import json
import datetime

db = SQLAlchemy()

class JSONEncodedDict(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False)
    rates = db.Column(JSONEncodedDict, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))