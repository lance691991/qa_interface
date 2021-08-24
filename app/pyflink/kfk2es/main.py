import os
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.common import Row
# from pyflink.table import TableFunction
# from pyflink.table.udf import udtf
from pyflink.table import ScalarFunction
from pyflink.table.udf import udf
from pyflink.datastream import StreamExecutionEnvironment
from parsers import RegexBaseParser
from pyflink.table.expressions import col
import json

cols = [str(i) + "c" for i in range(32)]

env = StreamExecutionEnvironment.get_execution_environment()
env_settings = EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
t_env = StreamTableEnvironment.create(env, environment_settings=env_settings)
t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)

jars = []
for file in os.listdir(os.path.abspath(os.path.dirname(__file__))):
    if file.endswith('.jar'):
        jars.append(os.path.abspath(file))
str_jars = ';'.join(['file://' + jar for jar in jars])
t_env.get_config().get_configuration().set_string("pipeline.jars", str_jars)


class CustomRegexParse(ScalarFunction):
    def __init__(self):
        class CustomRegexParser(RegexBaseParser):
            @classmethod
            def name(cls) -> str:
                return "nginx regex"

            @classmethod
            def grok_pattern(cls) -> str:
                return "\<%{INT}\>%{WORD}:%{TIMESTAMP_ISO8601};%{WORD}:%{WORD:event_level};%{WORD}:%{DATA};%{WORD}:%{DATA:event_content};%{WORD}:%{IP:src_ip};%{WORD}:%{INT:src_port};%{WORD}:%{IP:dst_ip};%{WORD}:%{INT:dst_port};%{WORD}:%{DATA};%{WORD}:%{DATA};%{WORD}:%{GREEDYDATA:protocol}"

        self.parser = CustomRegexParser()

        def unpack_parsed_dict(result):
            result_list = list(json.loads(result.json(ensure_ascii=False)).get('message_info', {}).values())

            def unpack_ip_info(index):
                if isinstance(result_list[index], dict):
                    dict_values = list(result_list[index].values())
                    del result_list[index]
                    if isinstance(dict_values[-1], dict):
                        location = list(dict_values[-1].values())
                        for v in location.reverse():
                            result_list.insert(index, v)
                    else:
                        for i in range(2):
                            result_list.insert(index, None)
                    for v in dict_values[: -1].reverse():
                        result_list.insert(index, v)
                else:
                    for i in range(8):
                        result_list.insert(index, None)

            unpack_ip_info(1)
            unpack_ip_info(12)

            return result_list

        self.unpacker = unpack_parsed_dict

    def eval(self, m_row):
        message = m_row[0]
        result = self.parser.parse(message)
        result = self.unpacker(result)
        if result[-1]:
            result[-1] = result[-1].strftime("%m/%d/%Y, %H:%M:%S")
        # raise NameError(str(result))
        return result
        # return result
custom_regex_parse = udf(CustomRegexParse(), result_type=DataTypes.ROW([DataTypes.FIELD("src_ip", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_country", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_province", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_city", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_distinct", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_street", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_postal_code", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_isp", DataTypes.STRING()),
                                                                        DataTypes.FIELD("src_ip_info_location_lat", DataTypes.FLOAT()),
                                                                        DataTypes.FIELD("src_ip_info_location_lon", DataTypes.FLOAT()),
                                                                        DataTypes.FIELD("src_port", DataTypes.INT()),
                                                                        DataTypes.FIELD("dst_ip", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_country", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_province", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_city", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_distinct", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_street", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_postal_code", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_isp", DataTypes.STRING()),
                                                                        DataTypes.FIELD("dst_ip_info_location_lat", DataTypes.FLOAT()),
                                                                        DataTypes.FIELD("dst_ip_info_location_lon", DataTypes.FLOAT()),
                                                                        DataTypes.FIELD("dst_port", DataTypes.INT()),
                                                                        DataTypes.FIELD("transport_protocol", DataTypes.STRING()),
                                                                        DataTypes.FIELD("application_protocol", DataTypes.STRING()),
                                                                        DataTypes.FIELD("url", DataTypes.STRING()),
                                                                        DataTypes.FIELD("event_level", DataTypes.TINYINT()),
                                                                        DataTypes.FIELD("event_category", DataTypes.STRING()),
                                                                        DataTypes.FIELD("event_type", DataTypes.STRING()),
                                                                        DataTypes.FIELD("event_id", DataTypes.STRING()),
                                                                        DataTypes.FIELD("event_name", DataTypes.STRING()),
                                                                        DataTypes.FIELD("event_content", DataTypes.STRING()),
                                                                        DataTypes.FIELD("stat_time", DataTypes.STRING())]))

# custom_regex_parse = udtf(CustomRegexParse(), result_types=[DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.FLOAT(),
#                                                                         DataTypes.FLOAT(),
#                                                                         DataTypes.TINYINT(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.FLOAT(),
#                                                                         DataTypes.FLOAT(),
#                                                                         DataTypes.TINYINT(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.TINYINT(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING(),
#                                                                         DataTypes.STRING()])

t_env.execute_sql(f"""
    CREATE TABLE source (
        message STRING
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'test',
        'properties.bootstrap.servers' = '127.0.0.1:9092',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'latest-offset',
        'json.fail-on-missing-field' = 'false',
        'json.ignore-parse-errors' = 'true',
        'format' = 'json'
    )
""")

t_env.execute_sql(f"""
CREATE TABLE sink (src_ip STRING,
    src_ip_info_country STRING,
    src_ip_info_province STRING,
    src_ip_info_city STRING,
    src_ip_info_distinct STRING,
    src_ip_info_street STRING,
    src_ip_info_postal_code STRING,
    src_ip_info_isp STRING,
    src_ip_info_location_lat FLOAT,
    src_ip_info_location_lon FLOAT,
    src_port INT,
    dst_ip STRING,
    dst_ip_info_country STRING,
    dst_ip_info_province STRING,
    dst_ip_info_city STRING,
    dst_ip_info_distinct STRING,
    dst_ip_info_street STRING,
    dst_ip_info_postal_code STRING,
    dst_ip_info_isp STRING,
    dst_ip_info_location_lat FLOAT,
    dst_ip_info_location_lon FLOAT,
    dst_port INT,
    transport_protocol STRING,
    application_protocol STRING,
    url STRING,
    event_level TINYINT,
    event_category STRING,
    event_type STRING,
    event_id STRING,
    event_name STRING,
    event_content STRING,
    stat_time STRING
) with (
    'connector' = 'kafka',
    'topic' = 'sink',
    'properties.bootstrap.servers' = '127.0.0.1:9092',
    'scan.startup.mode' = 'latest-offset',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true',
    'format' = 'json'
)
""")

# table API
source = t_env.from_path("source").select(col("message"))
# source.to_pandas()
# source.print_schema()
inter = source.map(custom_regex_parse)
# inter = inter.select(col('_c0'))
inter.print_schema()
inter.execute_insert("sink")
# source.execute_insert("sink")
# inter_table = source.select(custom_regex_parse(source.message))
# inter_table = inter_table.select(col("_c0"))
# inter_table.print_schema()
# inter_table.execute_insert("sink").wait()

# sql API
# t_env.sql_query("""
# SELECT
#     custom_regex_parse(message) AS
#     src_ip,
#     src_ip_info_country,
#     src_ip_info_province,
#     src_ip_info_city,
#     src_ip_info_distinct,
#     src_ip_info_street,
#     src_ip_info_postal_code,
#     src_ip_info_isp,
#     src_ip_info_location_lat,
#     src_ip_info_location_lon,
#     src_port,
#     dst_ip,
#     dst_ip_info_country,
#     dst_ip_info_province,
#     dst_ip_info_city,
#     dst_ip_info_distinct,
#     dst_ip_info_street,
#     dst_ip_info_postal_code,
#     dst_ip_info_isp,
#     dst_ip_info_location_lat,
#     dst_ip_info_location_lon,
#     dst_port,
#     transport_protocol,
#     application_protocol,
#     url,
#     event_level,
#     event_category,
#     event_type,
#     event_id,
#     event_name,
#     event_content,
#     stat_time
# FROM
#     source
# """).insert_into("sink")
# t_env.execute('test')

# t_env.from_path('source') \
#     .select('message, custom_regex_parse(message) AS src_ip,'
#             'src_ip_info_country,'
#             'src_ip_info_province,'
#             'src_ip_info_city,'
#             'src_ip_info_distinct,'
#             'src_ip_info_street,'
#             'src_ip_info_postal_code,'
#             'src_ip_info_isp,'
#             'src_ip_info_location_lat,'
#             'src_ip_info_location_lon,'
#             'src_port,'
#             'dst_ip,'
#             'dst_ip_info_country,'
#             'dst_ip_info_province,'
#             'dst_ip_info_city,'
#             'dst_ip_info_distinct,'
#             'dst_ip_info_street,'
#             'dst_ip_info_postal_code,'
#             'dst_ip_info_isp,'
#             'dst_ip_info_location_lat,'
#             'dst_ip_info_location_lon,'
#             'dst_port,'
#             'transport_protocol,'
#             'application_protocol,'
#             'url,'
#             'event_level,'
#             'event_category,'
#             'event_type,'
#             'event_id,'
#             'event_name,'
#             'event_content,'
#             'stat_time').select('src_ip,'
#                                 'src_ip_info_country,'
#                                 'src_ip_info_province,'
#                                 'src_ip_info_city,'
#                                 'src_ip_info_distinct,'
#                                 'src_ip_info_street,'
#                                 'src_ip_info_postal_code,'
#                                 'src_ip_info_isp,'
#                                 'src_ip_info_location_lat,'
#                                 'src_ip_info_location_lon,'
#                                 'src_port,'
#                                 'dst_ip,'
#                                 'dst_ip_info_country,'
#                                 'dst_ip_info_province,'
#                                 'dst_ip_info_city,'
#                                 'dst_ip_info_distinct,'
#                                 'dst_ip_info_street,'
#                                 'dst_ip_info_postal_code,'
#                                 'dst_ip_info_isp,'
#                                 'dst_ip_info_location_lat,'
#                                 'dst_ip_info_location_lon,'
#                                 'dst_port,'
#                                 'transport_protocol,'
#                                 'application_protocol,'
#                                 'url,'
#                                 'event_level,'
#                                 'event_category,'
#                                 'event_type,'
#                                 'event_id,'
#                                 'event_name,'
#                                 'event_content,'
#                                 'stat_time').execute_insert('sink')
