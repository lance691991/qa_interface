from typing import Union
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta

# Shared properties
class LogBase(BaseModel):
    timestamp: Union[date, datetime, time, timedelta]
    source_ip: str
    dest_ip: str
    direction: str
    protocol: str
    content: str
    period: float
    producer_ip: str
    producer_type: str
    type: str

