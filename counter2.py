import boto3
import csv
from datetime import datetime

def get_lambda_details(region, vpc_id, access_key, secret_key):
    client = boto3.client('lambda', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    lambdas = []
    response = client.list_functions()
    for function in response['Functions']:
        function_details = {
            'Name': function['FunctionName'],
            'Tags': ', '.join([f"{k}: {v}" for k, v in client.list_tags(Resource=function['FunctionArn'])['Tags'].items()]),
            'Versions': client.list_versions_by_function(FunctionName=function['FunctionName'])['Versions'],
            'CreatedDate': function.get('CreationTime', 'N/A')
        }
        if isinstance(function_details['CreatedDate'], str):
            function_details['CreatedDate'] = function_details['CreatedDate']
        else:
            function_details['CreatedDate'] = function_details['CreatedDate'].strftime('%Y-%m-%d %H:%M:%S')
        
        aliases = client.list_aliases(FunctionName=function['FunctionName'])
        function_details['Aliases'] = ', '.join([alias['Name'] for alias in aliases['Aliases']])
        lambdas.append(function_details)
    return lambdas

def get_api_gateway_details(region, vpc_id, access_key, secret_key):
    client = boto3.client('apigateway', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    apis = client.get_rest_apis()
    api_details = []
    for api in apis['items']:
        api_id = api['id']
        tags = ', '.join([f"{k}: {v}" for k, v in client.get_tags(resourceArn=f'arn:aws:apigateway:{region}::/restapis/{api_id}')['tags'].items()])
        api_details.append({'Name': api['name'], 'Tags': tags})
    return api_details

'''def get_dynamodb_details(region, vpc_id, access_key, secret_key):
    client = boto3.client('dynamodb', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    tables = client.list_tables()
    table_details = []
    for table_name in tables['TableNames']:
        tags = ', '.join([f"{k}: {v}" for k, v in client.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{region}::table/{table_name}')['Tags'].items()])
        table_details.append({'Name': table_name, 'Tags': tags})
    return table_details
'''
def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Tags', 'Versions', 'CreatedDate', 'Aliases']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def main():

    lambda_details = get_lambda_details(region, vpc_id, access_key, secret_key)
    api_gateway_details = get_api_gateway_details(region, vpc_id, access_key, secret_key)
#    dynamodb_details = get_dynamodb_details(region, vpc_id, access_key, secret_key)

    write_to_csv(lambda_details, 'lambda_details.csv')
    write_to_csv(api_gateway_details, 'api_gateway_details.csv')
 #   write_to_csv(dynamodb_details, 'dynamodb_details.csv')

if __name__ == "__main__":
    main()
