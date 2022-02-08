#This function is used to get competition list when the user clicks on the competitions tab on the side bar 

import json
import boto3
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection
import os
from aws_requests_auth.aws_auth import AWSRequestsAuth
import sys
import subprocess
import requests

def lambda_handler(event, context):
    # TODO implement
    
    
    ###HARD CODED###
    # competition_name='Competition_2'
    # ###############
    
    # #get all the competitions from ES
    
    host="search-fantastock0-23vzis4fs4cnwijmzo5e46qpza.us-west-2.es.amazonaws.com"
    awsauth = AWSRequestsAuth(aws_access_key='AKIAWEJK7I4J2XW4AGFS',
                      aws_secret_access_key='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',
                      aws_host=host,
                      aws_region='us-west-2',
                      aws_service='es')
    
    esClient = Elasticsearch(
        hosts=[{'host': host, 'port':443}],
        use_ssl=True,
        http_auth=awsauth,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
        
    searchData = esClient.search(index="competitions", body={"query":{"match_all":{}}})
    
    competitions=[]
    
    for competition in searchData['hits']['hits']:
        competitions.append(competition['_source'])

    
    if not competitions:
        return{
            'statusCode':200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No Competitions found')
        }
    else:    
        return{
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body': competitions,
            'isBase64Encoded': False
        }
    
    # searchData=searchData['hits']
    # print(searchData)
