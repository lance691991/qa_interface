import sys
sys.path.append("../")
from end2end.qa_end import QAEnd2End
from pyserini.search.lucene import LuceneSearcher
from pyserini.search.faiss import FaissSearcher, AutoQueryEncoder
from transformers import AutoModelForQuestionAnswering,AutoTokenizer,pipeline


class Query:
    def __init__(self, dense_searcher, sparse_searcher, qa_pipeline):
        self.qa = QAEnd2End(dense_searcher, sparse_searcher, qa_pipeline)

    def query(self, query_input):
        qa_result, hybrid_search_result = self.qa.qa(query_input)
        return qa_result, hybrid_search_result


s_searcher = LuceneSearcher('../indexes/sparse_index')
s_searcher.set_language('zh')
encoder = AutoQueryEncoder('../models/shibing')
d_searcher = FaissSearcher(
    '../indexes/shibing_index',
    encoder
)
model = AutoModelForQuestionAnswering.from_pretrained('../models/reader/luhua_mrc')
tokenizer = AutoTokenizer.from_pretrained('../models/reader/luhua_mrc')
QA = pipeline('question-answering', model=model, tokenizer=tokenizer)

qa_system = Query(d_searcher, s_searcher, QA)
