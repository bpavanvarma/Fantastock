
#----------------------------------------------------------------------------
# Created By  :  Pavan Varma  & Abhi Dasari
# Created Date: 12/23/2021
# version ='1.0'
# ---------------------------------------------------------------------------

import pymongo
from elasticsearch import Elasticsearch
from datetime import datetime as dt
from pytz import timezone
import utils 


def date_to_string(date):
    return date.strftime("%Y-%m-%d")

def calculateScore(investedstocks,startdate,enddate,stocks):
    avggain=-101
    iv=100
    fi=0
    investment=iv/len(investedstocks)

    for sym in investedstocks:
        oprice=10
        cprice=10.5
        try:
            oprice=stocks[sym]['prices'][startdate]["open"]
            cprice=stocks[sym]['prices'][enddate]["close"]
        except Exception:
            j=0 
        print(sym,oprice,cprice)
        if oprice ==0 or cprice==0:
            oprice=oprice+0.1
            cprice=cprice+0.1
        stockquantity=investment/oprice
        fi+=stockquantity*cprice
    score=round(((fi-iv)/iv)*100,2)
    return score


def scores(stocks,investedstocks,a,b):
    start=""
    end=""
    tz = timezone('EST')
    dateTimeObj = dt.now()
    aDateObj = dt.strptime(a, "%Y-%m-%d")
    if aDateObj>=dateTimeObj:
        aDateObj=dateTimeObj
    startdate=date_to_string(aDateObj)
    enddate=date_to_string(dateTimeObj)
    return calculateScore(investedstocks,startdate,enddate,stocks)



esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))
doc = {'query': {'match_all' : {}}}
res = es.search(index='competitions', body=doc)
userindex={}

reqstocks=[]
for competition in res['hits']['hits']:
    if competition['_source']['status'].lower() == "live":
        compRankings=competition['_source']['rankings']
        for user in compRankings.keys():
            temp=compRankings[user]
            reqstocks.extend(temp['stocks'])

utils.updatestocks(reqstocks)

client = pymongo.MongoClient("mongodb+srv://admin:admin123@fantastock.h4npu.mongodb.net/fanta_stock?retryWrites=true&w=majority")
db = client.fanta_stock
collection=db.stockdata
stocks={}
stocksdata=collection.find({'name': { '$in':reqstocks}})
for doc in stocksdata:
    stocks[doc["name"]]=doc

for competition in res['hits']['hits']:
    compid=competition['_id']
    competition=competition['_source']
    if competition['status'].lower() == "live":
        ranks={}
        compstartdate=competition['attributes']['startdate']
        compenddate=competition['attributes']['enddate']
        compRankings=competition['rankings']
        userranks={}
        userdata={}
        for user in compRankings.keys():
            temp=compRankings[user]
            score=scores(stocks,temp['stocks'],compstartdate,compenddate)
            userranks[user]=score
            temp['score']=score
            userdata[user]=temp
        sortUsers = sorted(userranks.items(), key=lambda x: x[1], reverse=True)
        count=1
        for i in sortUsers:
            userdata[i[0]]['score']=i[1]
            userdata[i[0]]['rank']=count
            if i[0] in userindex.keys():
                userindex[i[0]][compid]=userdata[i[0]]
            else:
                userindex[i[0]]={}
                userindex[i[0]][compid]=userdata[i[0]]
            count=count+1
        body={
                "script": {
                "lang": "painless",
                "source": """
                    ctx._source.rankings=params
                """,
                "params": userdata
                }
            }
        res= es.update(index="competitions", id=compid, body=body)
        print(userdata)
for userid in userindex.keys():
    body={
        "script": {
            "lang": "painless",
            "source": """
                Map comps=ctx._source.competitions;
                for (key in params.keySet()) {
                     comps[key]=params[key];
                }
            """,
            "params": userindex[userid]
        }
    }
    res= es.update(index="user", id=userid, body=body)   


utils.updatestatus()





