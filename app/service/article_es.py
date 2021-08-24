import app.model.Article
from elasticsearch_dsl import Document 
class Article(app.model.Article):
    def save(self,**kwargs):
        return Document.save(**kwargs)
