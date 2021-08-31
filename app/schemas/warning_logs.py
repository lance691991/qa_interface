from typing import Union
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta
from enum import Enum

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

class LogClassEnum(str, Enum):
    COMPREHENSIVE: "comprehensive"
    TODAY: "today"
    NEW_ASSET: "new_asset"
    ASSET_VULNERABILITY: "asset_vulneralbility"
    PROBE_SECURITY: "probe_security"
    PROBE_CONTROL: "probe_control"
    PROBE_SERVICE: "probe_service"
    MANAGE_PERFORMANCE: "manage_performance"
    WORK_PLAN: "work_plan"
