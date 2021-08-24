import datetime
import typing
import copy
import abc
import json
import pygrok
import enum
from pydantic import BaseModel, Field, IPvAnyAddress, AnyUrl


# ************ Log Item Schema ************
class LogSourceInfoSchema(BaseModel):
    """Log Source Info"""

    ip: IPvAnyAddress  # IP
    org_id: typing.Optional[str]  # 部署公司ID，此ID应和平台本身组织ID保持一致
    org_name: typing.Optional[str]

    device_model: typing.Optional[str]  # 设备型号
    device_vendor: typing.Optional[str]  # 设备厂商
    device_type: typing.Optional[str]  # 设备类型，如：防火墙、IPS、交换机等


class LocationSchema(typing.NamedTuple):
    """Location"""

    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)


class IpInfoInnerSchema(BaseModel):
    """IP Info"""

    country: typing.Optional[str]
    province: typing.Optional[str]
    city: typing.Optional[str]
    distinct: typing.Optional[str]
    street: typing.Optional[str]
    postal_code: typing.Optional[str]
    isp: typing.Optional[str]
    location: typing.Optional[LocationSchema]


class EventTypeEnum(str, enum.Enum):
    """Event Type"""

    UNKNOWN = "unknown"


class EventCategoryEnum(str, enum.Enum):
    """Event Category"""

    UNKNOWN = "unknown"


class LogMessageInfoSchema(BaseModel):
    """Log Message Info"""

    src_ip: typing.Optional[IPvAnyAddress]
    src_ip_info: typing.Optional[IpInfoInnerSchema]
    src_port: typing.Optional[int] = Field(None, ge=0, le=65535)
    dst_ip: typing.Optional[IPvAnyAddress]
    dst_ip_info: typing.Optional[IpInfoInnerSchema]
    dst_port: typing.Optional[int] = Field(None, ge=0, le=65535)
    transport_protocol: typing.Optional[str]  # Such as: TCP/UDP
    application_protocol: typing.Optional[str]  # Such as: HTTP/FTP/SSH
    url: typing.Optional[AnyUrl]
    event_level: int = 1
    event_category: EventCategoryEnum = EventCategoryEnum.UNKNOWN
    event_type: EventTypeEnum = EventTypeEnum.UNKNOWN
    event_id: typing.Optional[str]
    event_name: typing.Optional[str]
    event_content: typing.Optional[str]
    stat_time: typing.Optional[datetime.datetime]  # Log record time


class ParserTypeEnum(str, enum.Enum):
    """Parser Type"""

    JSON = "json"
    KV = "kv"
    REGEX = "regex"


class ParseInfoSchema(BaseModel):
    """Parse Info"""

    parser_type: ParserTypeEnum
    parser_name: str

    parse_time: datetime.datetime = datetime.datetime.now()
    parse_info: typing.Optional[str]
    parse_status: bool = True


class LogItemSchema(BaseModel):
    """Standard Log Item"""

    message: str
    message_info: typing.Optional[LogMessageInfoSchema]
    source_info: typing.Optional[LogSourceInfoSchema]
    parse_info: ParseInfoSchema


# ************ Base Parser ************
class BaseParser(abc.ABC):
    """Base Parser"""

    type: typing.ClassVar[typing.Optional[ParserTypeEnum]] = None
    mapping = {}  # Form as: {'data.a.b': 'schema_key'}

    def __init__(self, source_info: typing.Optional[LogSourceInfoSchema] = None):

        if not self.name().strip():
            raise ValueError(f"parser name must not be empty")

        if self.type is None:
            raise ValueError(f"parser type must not be empty")

        self.source_info = source_info

    def _get_parse_info(self, exc: typing.Optional[Exception] = None) -> ParseInfoSchema:

        return ParseInfoSchema(
            parser_type=self.type,
            parser_name=self.name(),
            parse_time=datetime.datetime.now(),
            parse_info=str(exc) if exc else None,
            parse_status=True if exc is None else False
        )

    def _standardize_log_item(self, data: dict, overwrite: bool = True) -> LogMessageInfoSchema:
        """Standardize log item"""

        result = copy.deepcopy(data)
        if self.mapping and isinstance(self.mapping, dict):
            for data_key, schema_key in self.mapping.items():
                try:
                    v = data
                    for key in data_key.split('.'):
                        if not key.strip():
                            raise KeyError

                        v = v[key]
                except Exception:
                    # Skip no exist or no valid key
                    continue
                else:
                    # Skip exist key in result when no overwrite
                    if not overwrite and schema_key in result:
                        continue

                    result[schema_key] = v

        return LogMessageInfoSchema(**result)

    def parse(self, message: str) -> LogItemSchema:
        """Parse message"""

        result = {'message': message, 'source_info': self.source_info}
        try:
            message_info = self.parse_message(message=message)
            result['message_info'] = self._standardize_log_item(message_info)
        except Exception as e:
            result['message_info'] = None
            result['parse_info'] = self._get_parse_info(e)
        else:
            result['parse_info'] = self._get_parse_info()

        return LogItemSchema(**result)

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Parser instance name"""

        raise NotImplementedError

    @abc.abstractmethod
    def parse_message(self, message: str) -> dict:
        """Parser parse message method"""

        raise NotImplementedError


# ************ Specific Parser ************
class JSONBaseParser(BaseParser, metaclass=abc.ABCMeta):
    """JSON Parser"""

    type = ParserTypeEnum.JSON

    def parse_message(self, message: str) -> dict:
        return json.loads(message)


class RegexBaseParser(BaseParser, metaclass=abc.ABCMeta):
    """Regex Parser"""

    type = ParserTypeEnum.REGEX

    def __init__(self, source_info: typing.Optional[LogSourceInfoSchema]=None):
        super().__init__(source_info=source_info)

        if not self.grok_pattern().strip():
            raise ValueError(f"grok pattern must not be empty")

    def parse_message(self, message: str) -> dict:
        grok = pygrok.Grok(self.grok_pattern())
        result = grok.match(message)

        # 解析失败
        if result is None:
            raise ValueError

        return result

    @classmethod
    @abc.abstractmethod
    def grok_pattern(cls) -> str:

        raise NotImplementedError


class KVBaseParser(BaseParser, metaclass=abc.ABCMeta):
    """Key-Value Base Parser"""

    type = ParserTypeEnum.KV

    def _judge_time_field(self, field):
        """判断时间内容"""

        if self.content_separator().strip() == ':' and field.count(':') == 2 \
            and all([i.isdigit() for i in field.split(self.content_separator())]):
            return True
        return False

    def _judge_last_field_include_content_separator(self, correct_fields):
        """判断前一field含有content separator"""

        if len(correct_fields) > 0 and correct_fields[-1].find(self.content_separator()) != -1:
            return True

        return False

    def _correct_field_split(self, message_fields):
        """纠正分割错误"""

        correct_fields = []
        for field in message_fields:
            if self.content_separator() is None:
                # 判断是否存在空白符
                if len(field.split()) > 1:
                    correct_fields.append(field)
                    continue
            else:
                # 判断是否有content separator
                if field.count(self.content_separator()) > 0:

                    # 排除时间异常分割和field合并问题
                    if not self._judge_time_field(field) and self._judge_last_field_include_content_separator(
                        correct_fields
                    ):
                        correct_fields.append(field)
                        continue

            # 进行field 合并
            if len(correct_fields) == 0:
                correct_fields.append(field)
            else:
                last_field = correct_fields.pop()
                if self.field_separator() is None:
                    correct_fields.append(' '.join([last_field, field]))
                else:
                    correct_fields.append(self.field_separator().join([last_field, field]))

        return correct_fields

    def parse_message(self, message):
        """Parse message

        思路：1. 先按field separator分割
             2. 其次按conent separator进行分割纠正
        """

        message_fields = message.split(sep=self.field_separator())
        # 仅日志内容，无key信息
        if self.content_separator() == '':
            return json.dumps(dict(enumerate(message_fields)))

        # 日志key-value
        result = {}

        # Correct error split
        correct_message_fields = self._correct_field_split(message_fields=message_fields)

        # 分割content
        for field in correct_message_fields:
            field_list = field.split(sep=self.content_separator())
            if len(field_list) >= 2:
                join_separator = ' ' if self.content_separator() is None else self.content_separator()
                result[field_list[0].strip()] = join_separator.join(field_list[1:]).strip()
            else:
                # 分割异常
                print(f'field content `{field}` split error by `{self.content_separator()}`.')
                continue

        if not result:
            raise ValueError(f"parse failed")
        return result

    @classmethod
    @abc.abstractmethod
    def field_separator(cls) -> typing.Optional[str]:

        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def content_separator(cls) -> typing.Optional[str]:

        raise NotImplementedError


if __name__ == '__main__':
    class CustomJSONParser(JSONBaseParser):

        mapping = {
            'a': 'src_port'
        }

        @classmethod
        def name(cls) -> str:
            return "custom json parser"

    class NginxRegexJsonParser(RegexBaseParser):

        @classmethod
        def name(cls) -> str:
            return "nginx regex"

        @classmethod
        def grok_pattern(cls) -> str:
            return "\<%{INT}\>%{WORD}:%{TIMESTAMP_ISO8601};%{WORD}:%{WORD:event_level};%{WORD}:%{DATA};%{WORD}:%{DATA:event_content};%{WORD}:%{IP:src_ip};%{WORD}:%{INT:src_port};%{WORD}:%{IP:dst_ip};%{WORD}:%{INT:dst_port};%{WORD}:%{DATA};%{WORD}:%{DATA};%{WORD}:%{GREEDYDATA:protocol}"



    result = NginxRegexJsonParser().parse("<5>time:2020-04-21 07:14:27;danger_degree:2;breaking_sighn:0;event:[50575]向日葵远程控制软件连接服务器;src_addr:10.30.3.178;src_port:33668;dst_addr:47.111.183.245;dst_port:443;user:;smt_user:;proto:SSL")
    print(result)
    print(result.dict().get('message_info', {}))
    print(list(json.loads(result.json(ensure_ascii=False)).get('message_info', {}).values()))
    print(json.loads(result.json(ensure_ascii=False)).get("message_info", {}))
    # parser = NginxJSONParser(source_info={'ip': '127.0.0.1', 'org_id': 1})
    # r = parser.parse('{"a": 1}')
    # print(r.dict(exclude_unset=True))
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

    print(unpack_parsed_dict(result))
