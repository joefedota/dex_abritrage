import requests
import json
import pickle
from dydx3 import Client
def uni_sushi_swap(endpoint):
    #endpoint = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    headers = {}
    #need to increment skip in order to get more than first 1000 pairs
    skip = 0
    tuples = []
    seen = set()
    while True:
        print(skip)
        query = """{
        pairs(first: 1000, skip: """ + str(skip) + """, orderBy: reserveUSD, orderDirection: desc) {
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
        #print(dic['data']['pairs'])
        if 'data' in dic:
            if len(dic['data']) == 0:
                break
            for pair in dic['data']['pairs']:
                if endpoint == "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2":
                    if (pair['token0']['symbol'], pair['token1']['symbol']) not in seen:
                        #some checks to eliminate any bogus data from the API calls
                        if pair['token0Price'] != '0' and pair['token1Price'] != '0' and pair['token0Price'] != pair['token1Price']:
                            tuples.append((pair['token0']['symbol'], pair['token1']['symbol'], pair['token0Price'], pair['token1Price'], "uni"))
                        seen.add((pair['token0']['symbol'], pair['token1']['symbol']))  
                else:
                    if (pair['token0']['symbol'], pair['token1']['symbol']) not in seen:
                        if pair['token0Price'] != '0' and pair['token1Price'] != '0' and pair['token0Price'] != pair['token1Price']:
                            tuples.append((pair['token0']['symbol'], pair['token1']['symbol'], pair['token0Price'], pair['token1Price'], "sushi"))
                        seen.add((pair['token0']['symbol'], pair['token1']['symbol']))
        else:
            break
        skip += 1000

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
            tuples.append(('ETH', dic['symbol'], 1/priceB, priceB, "kyber"))
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
        tups.append((mkt['baseAsset'], mkt['quoteAsset'], priceA, 1/priceA, "dydx"))
    write_market_state(tups, "dydx.pkl")
    return tups

def univ3():
    endpoint = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    headers = {}
    tuples = []
    skip = 0
    seen = set()
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
        #print(dic['data']['pairs'])
        if 'data' in dic:
            if len(dic['data']) == 0:
                break
            for pair in dic['data']['pools']:
                if (pair['token0']['symbol'], pair['token1']['symbol']) not in seen:
                    if pair['token0Price'] != '0' and pair['token1Price'] != '0' and pair['token0Price'] != pair['token1Price']:
                        tuples.append((pair['token0']['symbol'], pair['token1']['symbol'], pair['token0Price'], pair['token1Price'], "univ3"))
                    seen.add((pair['token0']['symbol'], pair['token1']['symbol']))
        else:
            break
        skip += 1000
    write_market_state(tuples, "univ3.pkl")
    return tuples


def write_market_state(tups, name):
    open_file = open(name, "wb")
    pickle.dump(tups, open_file)
    open_file.close()
#(token a, token b, token a price, token b price)