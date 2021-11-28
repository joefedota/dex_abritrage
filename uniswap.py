import requests
import json
import pickle
from dydx3 import Client
def uni_sushi_swap(endpoint):
    #endpoint = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    headers = {}
    #need to increment skip in order to get more than first 1000 pairs
    query = """{
    pairs(first: 1000, orderBy: reserveUSD, orderDirection: desc) {
        id
    }
    }"""

    r = requests.post(endpoint, json={"query": query}, headers=headers)

    data_json = json.loads(r.text)["data"]
    #print(data_json)
    #print(len(data_json))
    data = data_json['pairs']
    tuples = []
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
        r = requests.post(endpoint, json={"query": query}, headers=headers)
        dic = json.loads(r.text)
        tuples.append((dic['data']['pair']['token0']['symbol'], dic['data']['pair']['token1']['symbol'], dic['data']['pair']['token0Price'], dic['data']['pair']['token1Price']))

    if endpoint == "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2":
        write_market_state(tuples, "uni.pkl")
    else:
        write_market_state(tuples, "sushi.pkl")
    return tuples

def kyber():
    endpoint = "https://tracker.kyber.network/api/tokens/pairs"
    headers = {}
    query = {}
    r = requests.post(endpoint, json={"query": query}, headers=headers)
    data = json.loads(r.text)
    tuples = []
    for k, dic in data.items():
        priceB = float(dic['currentPrice'])
        if priceB:
            tuples.append(('ETH', dic['symbol'], 1/priceB, priceB))
    write_market_state(tuples, "kyber.pkl")
    return tuples

def dydx():
    #
    # Access public API endpoints.
    #
    public_client = Client(
        host='https://api.dydx.exchange',
    )
    mkts = public_client.public.get_markets()
    #print(mkts.data)
    tups = []
    for k, mkt in mkts.data['markets'].items():
        priceA = float(mkt['indexPrice'])
        tups.append((mkt['baseAsset'], mkt['quoteAsset'], priceA, 1/priceA))
    write_market_state(tups, "dydx.pkl")
    return tups

def write_market_state(tups, name):
    open_file = open(name, "wb")
    pickle.dump(tups, open_file)
    open_file.close()
#(token a, token b, token a price, token b price)