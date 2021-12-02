import requests
import json

endpoint = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
headers = {}
tuples = []
skip = 0
while True:
    print(skip)
    query = """{
    pools(first: 1000, skip: """ + str(skip) + """) {
        id
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
    r = requests.post(endpoint, json={"query": query}, headers=headers)
    dic = json.loads(r.text)
    #print(dic)
    #print(dic['data']['pairs'])
    if 'data' in dic:
        if len(dic['data']) == 0:
            break
        for pair in dic['data']['pools']:
            tuples.append((pair['token0']['symbol'], pair['token1']['symbol'], pair['token0Price'], pair['token1Price'], "univ3"))
    else:
        break
    skip += 1000