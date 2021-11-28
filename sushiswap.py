import requests
import json

endpoint = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"
headers = {}

query = """{
   pairs(first: 1000, orderBy: reserveUSD, orderDirection: desc) {
     id
   }
 }"""

r = requests.post(endpoint, json={"query": query}, headers=headers)

data_json = json.loads(r.text)["data"]

data = data_json['pairs']
responses = []
for pair in data:
    query = """{
   pair(id: \"""" + pair['id'] + """\"){
     token0 {
       id
       symbol
       name
       derivedETH
     }
     token1 {
       id
       symbol
       name
       derivedETH
     }
     token0Price
     token1Price
   }
   }"""
    responses.append(requests.post(endpoint, json={"query": query}, headers=headers))
print(responses[0].text)