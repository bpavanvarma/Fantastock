import json
from datetime import date
from elasticsearch import Elasticsearch

esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))

def storeloggedinuserinfo(userinfo):

    uid=userinfo['sub']
    doc={
          "name" : userinfo['name'],
          "userid" : uid,
          "dateofjoin" : str(date.today()),
          "coins" : 100,
          "competitions" : {}
    }
    res = es.index(index="user", id=uid, body=doc)
    
def lambda_handler(event, context):
    userinfo= event['request']['userAttributes']
    storeloggedinuserinfo(userinfo)
    print(userinfo)
    # Return to Amazon Cognito
    return event
