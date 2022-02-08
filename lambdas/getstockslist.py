
import pymongo
import json

def lambda_handler(event, context):
    
    sectors = dict({"Demo Competition":"Healthcare", "Demo Competition 1":"Healthcare"})

    competition=event['body-json']['competition']
    #e=json.loads(event)
    sector=""
    if 'sector' in event.keys():
        if event['sector']:
            sector=event['sector']

    if not sector : 
        sector = "Technology"
    if competition and competition in sectors.keys():
        sector =sectors[competition]
    client = pymongo.MongoClient("mongodb+srv://admin:admin123@fantastock.h4npu.mongodb.net/fanta_stock?retryWrites=true&w=majority")
    db = client.fanta_stock
    collection=db.stockdata
    myquery = {'sector':sector}
    mydoc = collection.find(myquery)
    stockslist=[]
    
    for stocks in mydoc:
        if 'name' in stocks.keys() and stocks['name'] and stocks['name'].lower() != 'null' :
            stockslist.append(stocks['name'])
    
    if not stockslist:
        return{
            'statusCode':200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No Companies found')
        }
    else:    
        stockslist.sort()
        return{
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body':stockslist,
            'isBase64Encoded': False
        }
