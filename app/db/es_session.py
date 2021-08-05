from elasticsearch_dsl import connections
from app.core.config import ES_SERVER


connections.create_connection(hosts=ES_SERVER)
