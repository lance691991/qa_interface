from app.service.base import WarningServiceBase
from app.schemas.warning_logs import LogBase
from app.models.warning_logs import WarningLogs
from app.models.warning_probes import WarningProbes
from app.models.warning_scannings import WarningScannings
from wisdoms.commons import success
import math

class ServiceWarningLogs(WarningServiceBase[LogBase, LogBase]):
    def get_by_page(self, db, current_page: int=1, load_per_page: int=10):
        try:
            s = super().get(db, index=WarningLogs.Index.name).sort("-stat_time")
            response = s.execute()
        except Exception as e:
            return e
        total = math.ceil(response.hits.total.value / load_per_page)
        response_dict = {
            "total": total,
            "current": current_page,
            "data": response[(current_page-1)*load_per_page: current_page*load_per_page]
        }
        return success(response_dict)

    def get_by_today(self, db):
        try:
            s = super().get(db=db, index=WarningLogs.Index.name)
            s = s.query('range', **{"stat_time": {"gte": "now/d", "lt": "now"}})
            response = s.execute()
        except Exception as e:
            return e
        return success(response)

    def add_probes(self, db, data):
        try:
            super().add(db=db, index=WarningProbes.Index.name, data=data)
        except Exception as e:
            return e
        return success(data)

    def add_scannings(self, db, data):
        try:
            super().add(db=db, index=WarningScannings.Index.name, data=data)
        except Exception as e:
            return e
        return success(data)

warning_logs = ServiceWarningLogs()
