# Using OpenSearch from Python
We will be using the `opensearch-py` module:
```
pip install opensearch-py
```

## Basic usage
First we have to import it
```python
from opensearchpy import OpenSearch
```

Creating a connection:
```python
host = 'localhost'
port = 9200
user = 'admin'
password = 'admin'

es = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,
    http_auth=(user, password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)
```

Creating an index:
```python
index_name = 'test'
index_body = {
  'settings': {
    'index': {
      'number_of_shards': 1,
      'number_of_replicas': 0
    }
  }
}

response = es.indices.create(index_name, body=index_body)

print(response)
```

Sending data:
```python
document = {
  'title': 'The Arrival',
  'year': '2016',
  'genres': ['Sci-fi', 'Action']
}
id = '1'

es.index(
    index = index_name,
    body = document,
    id = id,
    refresh = True
)
```

Searching:
```python
query = {
  'query': {
    'match': {
      'title': 'arrival'
    }
  }
}

response = es.search(
    body = query,
    index = index_name
)

print(response)
```

Delete a document
```python
response = es.delete(
    index = index_name,
    id = id
)

print(response)
```

Delete a index
```python
response = es.indices.delete(
    index = index_name
)

print(response)
```

## Reference
- [opensearch-py](https://opensearch.org/docs/latest/clients/python/)
- [elasticsearch-py](https://elasticsearch-py.readthedocs.io/en/v8.4.3/)

## Exercises
- Lab: Test the opensearch-py module from an interactive python session
    ```
    sudo dnf install python39
    pip install opensearch-py
    python3
    ```

- Lab: [Ingesting data from Twitter](exercises/twitter/twitter.md) 
 - Lab files are located in the `exercices/twitter` directory


