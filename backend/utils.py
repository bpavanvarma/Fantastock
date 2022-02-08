
#----------------------------------------------------------------------------
# Created By  :  Pavan Varma  & Abhi Dasari
# Created Date: 12/23/2021
# version ='1.0'
# ---------------------------------------------------------------------------


import pandas as pd
import yfinance as yf
import pymongo
from datetime import datetime
from yahoo_fin import stock_info as si
from elasticsearch import Elasticsearch
from pprint import pprint
from pytz import timezone
import yfinance as yf


def time_to_string(date):
    return date.strftime("%H:%M:%S")
def date_to_string(date):
    return date.strftime("%Y-%m-%d")

def updatestocks(stocklist):
    symbols=[]
    client = pymongo.MongoClient("mongodb+srv://admin:admin123@fantastock.h4npu.mongodb.net/fanta_stock?retryWrites=true&w=majority")
    db = client.fanta_stock
    collection=db.stockdata
    stocksdata=collection.find({'name': { '$in':stocklist}})
    for doc in stocksdata:
        symbols.append(doc["_id"])
    tz = timezone('EST')
    dateTimeObj = datetime.now(tz)
    timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")

    for sym in symbols:
        if sym:
            s=collection.find({"_id": sym}).limit(1)
            if(len(list(s.clone()))>0):
                print("Update :",sym)
                updaterecord=s[0]
                updaterecord["timestamp"]=timestampStr
                if "prices" not in updaterecord.keys():
                    updaterecord["prices"]={}
                data=yf.download(tickers=sym, period='1d', interval='1d')
                data=data.reset_index()
                for index, row in data.iterrows():
                    if (isinstance(row["Open"], float) or isinstance(row["Open"], int)) and (isinstance(row["Close"], float) or isinstance(row["Close"], int)) :
                        updaterecord["prices"][date_to_string(row["Date"])]={
                            "open":round(row["Open"],2),
                            "close":round(row["Close"],2)
                        }
                collection.replace_one({ "_id": sym},updaterecord,True)       
            else:
                print("insert :",sym)
                sector=""
                ticker = yf.Ticker(sym)
                temp=ticker.info
                if "sector" in temp.keys():
                    sector=temp["sector"]
                    if "shortName" in temp.keys():
                        stockname=temp["shortName"]
                        newrecord={}
                        newrecord["_id"]=sym
                        newrecord["name"]=stockname
                        newrecord["prices"]={}        
                        newrecord["timestamp"]=timestampStr
                        newrecord["sector"]=sector
                        newrecord["index"]="Dow Jones"
                        prices={}
                        data=yf.download(tickers=sym, period='10d', interval='1d')
                        data=data.reset_index()
                        for index, row in data.iterrows():
                            if (isinstance(row["Open"], float) or isinstance(row["Open"], int)) and (isinstance(row["Close"], float) or isinstance(row["Close"], int)) :
                                prices[date_to_string(row["Date"])]={
                                    "open":round(row["Open"],2),
                                    "close":round(row["Close"],2)
                                }
                        newrecord["prices"]=prices
                        collection.insert_one(newrecord)       


def updatestatus():
    esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
    es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))
    doc = {'query': {'match_all' : {}}}
    res = es.search(index='competitions', body=doc)
    for competition in res['hits']['hits']:
        status=""
        compid=competition['_id']
        competition=competition['_source']
        compstartdate=competition['attributes']['startdate']
        compenddate=competition['attributes']['enddate']
        dateTimeObj = datetime.now()
        compstartdate = datetime.strptime(compstartdate, "%Y-%m-%d")
        compenddate = datetime.strptime(compenddate, "%Y-%m-%d")
        if compstartdate<=dateTimeObj:
            if compenddate>=dateTimeObj:
                status="Live"
            else:
                status="Closed"
                updatecoins(competition)
        else:
            status="Yet to Start"
        
        if competition['status'].lower() != status.lower():
            body={
                "script": {
                "lang": "painless",
                "source": """
                    ctx._source.status=params.status
                """,
                "params": {"status":status}
                }
            }
            res= es.update(index="competitions", id=compid, body=body)


def updatecoins(competition):
    esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
    es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))
    rankdistribution={}
    temp=competition['distribution']
    for key in temp.keys():
        if ":" in key or "-" in key:
            spliter=""
            if ":" in key:
                spliter=":"
            else:
                spliter="-"
            keysplit=key.split(spliter)
            for i in range(int(keysplit[0]),int(keysplit[0])+1):
                rankdistribution[i]=int(temp[key])
        else:
            rankdistribution[int(key)]=int(temp[key])
    compRankings=competition['rankings']
    for userid in compRankings.keys():
        userrank=compRankings[userid]['rank']
        if userrank in rankdistribution.keys():
            body={
            "script": {
            "lang": "painless",
            "source": """
                ctx._source.coins+=params.coins;
            """,
            "params": {"coins":rankdistribution[userrank]}
                }
            }
            res= es.update(index="user", id=userid, body=body)
    

