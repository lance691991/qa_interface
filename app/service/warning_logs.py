from app.service.base import LogServiceBase
from app.schemas.warning_logs import LogBase
from app.models.warning_logs import WarningLogs
from elasticsearch_dsl import Q, Search

class ServiceWarningLogs(LogServiceBase[LogBase, LogBase]):
    def get_by_page(self, db, current_page: int=1, load_per_page: int=10):
        s = Search(using=db, index="ip_tags")
        response = s.execute()
        print("~~~~~~~~~~~", response)
        return response[(current_page-1)*load_per_page: current_page*load_per_page]
        # return s
warning_logs = ServiceWarningLogs()
