from typing import Type
from elasticsearch_dsl import connections

SessionES = connections.create_connection(hosts=["http://elastic:@127.0.0.1:9200"], timeout=20)
print(Type[SessionES])
