import json
import boto3
import requests
from elasticsearch import Elasticsearch

esurl="https://search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
es = Elasticsearch([esurl], http_auth=('admin', 'Admin@123'))

def lambda_handler(event, context):
    print(event)
    doc=event['body-json']
    accesstoken=doc['token']
    client = boto3.client('cognito-idp', region_name='us-west-2')
    response = client.get_user(
    AccessToken=accesstoken
    )
    
    print(response)
    name = response['Username']
    print(name)
    for attr in response['UserAttributes']:
        if attr['Name'] == 'sub':
            uid= attr['Value']
    
    query1 = {"query": {"match": {"_id": uid}}}
    es_result_user=es.search(index="user", body=query1)
    current_body = es_result_user['hits']['hits'][0]['_source']
    print(current_body)
    return{
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin":"*"},
        'body':current_body,
        'isBase64Encoded': False
        }
