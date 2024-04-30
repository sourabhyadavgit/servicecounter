import boto3
import csv


def get_lambda_details(region, vpc_id, access_key, secret_key):
    client = boto3.client('lambda', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    lambdas = []
    response = client.list_functions()
    for function in response['Functions']:
        function_details = {
            'Name': function['FunctionName'],
            'Tags': client.list_tags(Resource=function['FunctionArn'])['Tags'],
            'Versions': client.list_versions_by_function(FunctionName=function['FunctionName'])['Versions']
        }
        aliases = client.list_aliases(FunctionName=function['FunctionName'])
        function_details['Aliases'] = [alias['Name'] for alias in aliases['Aliases']]
        lambdas.append(function_details)
    return lambdas

def get_api_gateway_tags(region, vpc_id, access_key, secret_key):
    client = boto3.client('apigateway', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    apis = client.get_rest_apis()
    api_tags = {}
    for api in apis['items']:
        api_id = api['id']
        tags = client.get_tags(resourceArn=f'arn:aws:apigateway:{region}::/restapis/{api_id}')
        api_tags[api['name']] = tags['tags']
    return api_tags

'''def get_dynamodb_tags(region, vpc_id, access_key, secret_key):
    client = boto3.client('dynamodb', region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    tables = client.list_tables()
    table_tags = {}
    for table_name in tables['TableNames']:
        tags = client.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{region}::table/{table_name}')
        table_tags[table_name] = tags['Tags']
    return table_tags
'''
def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Service', 'Details'])
        for service, details in data.items():
            writer.writerow([service, details])

def main():
    

    lambda_details = get_lambda_details(region, vpc_id, access_key, secret_key)
    api_gateway_tags = get_api_gateway_tags(region, vpc_id, access_key, secret_key)
    #dynamodb_tags = get_dynamodb_tags(region, vpc_id, access_key, secret_key)

    data = {
        'Lambda Functions': lambda_details,
        'API Gateway APIs': api_gateway_tags
 #       'DynamoDB Tables': dynamodb_tags
    }

    write_to_csv(data, 'aws_services_details.csv')

if __name__ == "__main__":
    main()