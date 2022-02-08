from elasticsearch import Elasticsearch
import json
import boto3


esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))
"""
doc={
      "uid": "bpvarma",
      "cid": "Competition_2",
      "stocks": ["WBA","IBM","HD","GS","CAT"],
    }
    """
def lambda_handler(event, context):
    doc=event['body-json']
    stocks=doc["companies"]
    accesstoken=doc['token']
    competition=doc['competition']

    #query for user id using token (inturn user name) for updation   
    client = boto3.client('cognito-idp', region_name='us-west-2')
    uid=""
    response = client.get_user(
    AccessToken=accesstoken
    )
    
    name = response['Username']
 
    for attr in response['UserAttributes']:
        if attr['Name'] == 'sub':
            uid= attr['Value']


    doc={
      "uid": uid,
      "cid": competition,
      "stocks": stocks,
    }
    
#    doc={
  #      "uid": 'ba9eb99b-5100-43de-aa2f-fabbf78e8925', 
  #      "cid": 'DecMonthlyCompetition', 
 #       "stocks": ['Globant S.A.', 'Katapult Holdings, Inc.', 'Intellicheck, Inc.', 'Sigma Labs, Inc.', 'Cazoo Group Ltd']
 #   }

    print(doc)
    res={}
    
    if(es.exists(index="competitions", id=doc["cid"]) and es.exists(index="user", id=doc["uid"])):
        body={
            "script": {
            "lang": "painless",
            "source": """
                Map rankingDetails=ctx._source.rankings;

            if (rankingDetails.containsKey(params.uid.toString())) {
                    rankingDetails[params.uid.toString()]["stocks"]=params.stocks;
                    rankingDetails[params.uid.toString()]["changes"]+=1;
                }else{
                 Map temp=[:];
                 temp['score']=0;
                 temp['rank']=0;
                 temp['stocks']=params.stocks;
                 temp['changes']=0;
                 ctx._source.rankings[params.uid]=temp;
                }
            
            """,
            "params": doc
            }
        }
        res= es.update(index="competitions", id=doc["cid"], body=body)
    
        body={
            "script": {
            "lang": "painless",
            "source": """
                Map competitionsDetails=ctx._source.competitions;
                    if (competitionsDetails.containsKey(params.cid.toString())) {
                    competitionsDetails[params.cid.toString()]["stocks"]=params.stocks;
                    competitionsDetails[params.cid.toString()]["changes"]+=1;
                }else{
                    Map temp=[:];
                    temp['score']=0;
                    temp['rank']=0;
                    temp['stocks']=params.stocks;
                    temp['changes']=0;
                    ctx._source.competitions[params.cid]=temp;
                    ctx._source.coins-=10;
                }
            """,
            "params": doc
            }
        }
        res = es.update(index="user", id=doc["uid"], body=body)
    
    else:
        res['comp']={"msg":"Competition or User dosen't exists"}
    
    print(res)


"""from elasticsearch import Elasticsearch
import json
import boto3

esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))

def lambda_handler(event, context):
    companies={}
    
    doc=event['body-json']
    stocks=doc["companies"]
    
    for i in stocks:
        companies[i]=1
    
    
    accesstoken=doc['token']
    competition=doc['competition']

    #query for user id using token (inturn user name) for updation   
    client = boto3.client('cognito-idp', region_name='us-west-2')

    response = client.get_user(
    AccessToken=accesstoken
    )
    
    name = response['Username']
 
    for attr in response['UserAttributes']:
        if attr['Name'] == 'sub':
            uid= attr['Value']

    #query for current user and current competition
    query1 = {"query": {"match": {"_id": uid}}}
    query2 = {"query": {"match": {"Competitionid": competition}}}
 

    es_result_user=es.search(index="user", body=query1)
    es_result_competition=es.search(index="competitions", body=query2)
    es_result_user_id=es_result_user['hits']['hits'][0]['_id'] #can use this to update
    
    print(es_result_user, es_result_competition, es_result_user_id)

    
#USER SECTION: (NEED USER ID FOR UPDATION)
    #get user's current details
    current_body = es_result_user['hits']['hits'][0]['_source']
    
    # #update the coins only if the user has not registered for the competition yet
    if not competition in current_body['competitions']:
        current_body['coins']-=20 
    
    current_body['competitions']=companies
    
    # #update the user details
    es.update(index="user", id=es_result_user_id, body=current_body)
    

#COMPETITION SECTION:
    #get competition id
    competition_details=es_result_competition['hits']['hits'][0]
    competition_id=competition_details['_id']
    
    current_body=competition_details['_source']
    #everybody are in rank 1000 when they register
    current_body['rankings'][uid]=1000

    #update the competition
    res=es.update(index="competitions", id=competition_id, body=current_body)


    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }
    
    """
