from elasticsearch_dsl import Document, IpRange, Integer, Keyword, Text, Nested, Object, Date, Ip
from app.db.session import SessionES

class WarningScannings(Document):
    ip_range = IpRange()
    find_count = Integer()
    reason = Keyword()
    status_ = Text()
    cve_info = Nested()
    port_range = Keyword()
    masscan_info = Object()
    service_info = Object()
    type = Keyword()
    org_ = Nested()
    nmap_info = Object()
    mode = Keyword()
    updTime_ = Date()
    web_info = Object()
    user_ = Nested()
    action_time = Date()
    os_info = Object()
    port_status = Keyword()
    port_info = Object()
    vul_info = Nested()
    fofa_info = Nested()
    created_time = Date()
    ip = Ip()
    addTime_ = Date()
    end_time = Date()
    priority = Integer()
    ttl = Integer()
    version = Integer()
    org_info = Object()
    asset_info = Nested()
    start_time = Date()
    proto = Keyword()
    source_id = Keyword()
    domain_info = Object()
    sv_info = Nested()
    ip_info = Object()
    status = Keyword()

    class Index:
        name = 'warning_scannings'

if __name__ == '__main__':
    SessionES
    WarningScannings.init()