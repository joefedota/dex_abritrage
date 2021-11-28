import requests
import json
from dydx3 import Client

def kyber():
    endpoint = "https://tracker.kyber.network/api/tokens/pairs"
    headers = {}
    query = {}
    r = requests.post(endpoint, json={"query": query}, headers=headers)
    data = json.loads(r.text)
    tuples = []
    print(data)
    for k, dic in data.items():
        priceB = float(dic['currentPrice'])
        if priceB:
            tuples.append(('ETH', dic['symbol'], 1/priceB, priceB))
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
    return tups
    
dydx()
kyber()
#all of these will output a 4 tuple of form (token A, token B, price for A, price for B)
