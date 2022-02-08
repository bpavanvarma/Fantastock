import json
from elasticsearch import Elasticsearch

esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))

comid="Demo Competition 1" #MUST CHANGE THIS EVERYTIME!!!!
doc={
          "status" : "Yet to Start",
          "category" : "Mini",
          "type" : "Mini",
          "Competitionid" : comid,
          "attributes" : {
            "startdate" : "2021-12-19",
            "enddate" : "2021-12-26",
            "poolsize" : "5",
            "winners" : "2",
            "totalamount" : "40",
            "entryfee" : "10",
            "changes" : "0"
          },
          "distribution" : {
            "1" : 25,
            "2" : 15
          },
  'rankings': {} #current rankings
}


def updateonlydates(compid,sd,ed):
    body={
                "script": {
                "lang": "painless",
                "source": """
                    ctx._source.attributes.startdate=params.sd;
                    ctx._source.attributes.enddate=params.ed
                """,
                "params": {
                    "sd":sd,
                    "ed":ed
                }
                }
            }
    res= es.update(index="competitions", id=compid, body=body)

def lambda_handler(event, context):
    res={}
    res = es.index(index="competitions", id=comid, body=doc)
    #updateonlydates(comid,"2021-12-19","2021-12-22")
    #use this if you wanna delete competitions
    
    # query = {"query": {"match": {"Competitionid": '2022-MEGA'}}}
    # res = es.delete_by_query(index="competitions", body=query)
    
    return {
        'statusCode': 200,
        'msg': json.dumps(res)
    }
