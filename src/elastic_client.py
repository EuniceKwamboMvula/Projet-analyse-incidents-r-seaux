from elasticsearch import Elasticsearch


class ESClient:
def __init__(self, host='http://localhost:9200'):
self.es = Elasticsearch(hosts=[host])


def index_df(self, df, index_name):
records = df.to_dict(orient='records')
for r in records:
self.es.index(index=index_name, document=r)


def search(self, index, query, size=10000):
res = self.es.search(index=index, query=query, size=size)
return res