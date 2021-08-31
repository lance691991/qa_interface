from elasticsearch_dsl import Document, IpRange, Integer, Keyword, Text, Nested, Object, Date, Ip
from app.db.session import SessionES


class WarningProbes(Document):
    id = Text(fields={"keyword": Keyword()})
    ip = Text(fields={"keyword": Keyword()})
    func_code = Text(fields={"keyword": Keyword()})
    desc = Text(fields={"keyword": Keyword()})
    typeof = Text(fields={"keyword": Keyword()})
    user_ = Nested()
    org = Nested()
    addTime_ = Date()
    updTime_ = Date()
    status_ = Text(fields={"keyword": Keyword()})

    class Index:
        name = 'warning_probes'


if __name__ == '__main__':
    SessionES
    WarningProbes.init()