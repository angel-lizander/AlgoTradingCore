import json
from types import SimpleNamespace

def getConfigurations():
    f = open(r'config.dev.json')
    dataGet = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))
    return dataGet       

def getGeneralConfigurations():
    return getConfigurations().Configuration

def getStrategyConfigurations():
    return getConfigurations().Strategy

def getAccountsConfigurations():
    return getConfigurations().Accounts   

def getMarketConfigurations():
    return getConfigurations().Market
