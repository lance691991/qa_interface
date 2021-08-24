from elasticsearch_dsl import Document, Date, Keyword, Text, Float
from app.db.session import SessionES

class WarningLogs(Document):
    timestamp = Date()
    source_ip = Text()
    dest_ip = Text()
    direction = Keyword()
    protocol = Keyword()
    content = Text()
    period = Float()
    producer_ip = Keyword()
    producer_type = Keyword()
    type = Text()

    class Index:
        name = 'warning_logs'

if __name__ == '__main__':
    SessionES
    WarningLogs.init()
