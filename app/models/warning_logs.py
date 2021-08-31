from elasticsearch_dsl import Document, Date, Keyword, Text, Float, Integer
from app.db.session import SessionES

class WarningLogs(Document):
    src_ip = Text()
    src_ip_info_country = Text(),
    src_ip_info_province = Text()
    src_ip_info_city = Text()
    src_ip_info_distinct = Text()
    src_ip_info_street = Text()
    src_ip_info_postal_code = Text()
    src_ip_info_isp = Text()
    src_ip_info_location_lat = Float()
    src_ip_info_location_lon = Float()
    src_port = Integer()
    dst_ip = Text()
    dst_ip_info_country = Text()
    dst_ip_info_province = Text()
    dst_ip_info_city = Text()
    dst_ip_info_distinct = Text()
    dst_ip_info_street = Text()
    dst_ip_info_postal_code = Text()
    dst_ip_info_isp = Text()
    dst_ip_info_location_lat = Float()
    dst_ip_info_location_lon = Float()
    dst_port = Integer()
    transport_protocol = Text()
    application_protocol = Text()
    url = Text()
    event_level = Integer()
    event_category = Text()
    event_type = Text()
    event_id = Text()
    event_name = Text()
    event_content = Keyword()
    stat_time = Date()

    class Index:
        name = 'warning_logs'

if __name__ == '__main__':
    SessionES
    WarningLogs.init()
