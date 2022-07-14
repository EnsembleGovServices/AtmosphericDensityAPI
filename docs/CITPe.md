# Base endpoint: 

    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1



## Endpoint: /{bucket}
Request Methods: `GET`

Headers: `"X-API-Key"` : `API_KEYS`

Example **URL**:
    
    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data

Example **Response**: 
```yaml
{
    "start": 1,
    "limit": 10,
    "count": 999,
    "previous": "",
    "next": "?start=11&limit=10",
    "data": [
        "CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T00:20:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T00:30:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T00:40:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T00:50:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T01:00:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T01:10:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T01:20:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T01:30:00.parquet",
        "CTIPE_RHO_GEO_2022-05-13T01:40:00.parquet"
    ]
}
```


- Pass **next** or **previous** in the query to see the next files lists 

Example:

     https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data?start=11&limit=10


```python
import requests

headers = {'X-API-Key': 'API_KEY_HERE'}

request_url = 'https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data'

response = requests.get(request_url, headers=headers)

print(response.json())
```



## Endpoint: /{bucket}/{file}
Request Methods: `GET`

Headers: `"X-API-Key"` : `API_KEYS`


Example **URL**: 

    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data/CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet

Example **Response**:  This will download the file

```python
import requests

headers = {'X-API-Key': 'API_KEY_HERE'}

request_url = 'https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data/CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet'

response = requests.get(request_url, headers=headers)

with open('CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet', 'wb') as file:
    file.write(response.content)
```

- This will download the file from **S3** and store it in your local.
