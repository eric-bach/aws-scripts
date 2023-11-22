import datetime
import boto3
import json

F1_SG = "sg-0b4baaeedcc5c3dce"
M2_SG = "sg-01f3059a533b62208"
EXP_SG = "sg-06bc7733c60f6741e"
OMN_SG = "sg-06dcd4bc0a4eb5d7c"
CEH_SG = "sg-03fc49f78cfcd4de9"
SUBNET_1 = "subnet-0c97477b31b49f8be"
SUBNET_2 = "subnet-0351248ea92ee561e"
SUBNET_3 = "subnet-0f3dbaccd2c1fcf36"
SUBNET_4 = "subnet-0418853079ef7eb8a"
SG_SUBNETS = {
    F1_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4],
    M2_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4],
    EXP_SG: [SUBNET_1, SUBNET_2],
    OMN_SG: [SUBNET_1, SUBNET_2],
    CEH_SG: [SUBNET_1, SUBNET_2],
}

def get_lambda_function_details(function_name):
    lambda_client = boto3.client('lambda')

    try:
        # Get function configuration
        response = lambda_client.get_function_configuration(FunctionName=function_name)

        # Extract relevant details
        function_details = {
            'function_name': response['FunctionName'],
            'function_arn': response['FunctionArn'],
            'runtime': response['Runtime'],
            'memory_size': response['MemorySize'],
            'timeout': response['Timeout'],
            'last_modified': response['LastModified'],
            'subnet_ids': response.get('VpcConfig', {}).get('SubnetIds', []),
            'security_group_ids': response.get('VpcConfig', {}).get('SecurityGroupIds', []),
        }

        return function_details

    except lambda_client.exceptions.ResourceNotFoundException as e:
        print(f"❌ Lambda function '{function_name}' not found. Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error retrieving Lambda function details. Error: {e}")
        return None

def evaluate_compliance(configuration_item):
    resource_name = configuration_item['resourceName']
    function = get_lambda_function_details(resource_name)

    # Handle the cases when a Lambda function is deleted generates a CloudTrail event
    if function is None:
        print(f"{resource_name} not found or may have been deleted")
        return "COMPLIANT"

    # Get Security Group Id and Subnet Ids if they exist
    if function is not None:
        security_group_id = function['security_group_ids'][0] if len(function['security_group_ids']) > 0 else None
        subnet_ids = function['subnet_ids'] if len(function['subnet_ids']) > 0 else None

    print(f"Security Group Id: {security_group_id}")
    print(f"Subnet Ids: {subnet_ids}")

    if security_group_id is None or subnet_ids is None:
        print(f"✅ {resource_name} COMPLIANT - No VPC configuration")
        return "COMPLIANT"
    
    # Ignore Lambda functions in the staging or production environment (currently the only consistent way is by resource name since we don't tag consistently)
    resource_name = configuration_item.get("resourceName", "")
    if "staging" in resource_name or "prod" in resource_name or "securityscan" in resource_name:
        print(f"✅ {resource_name} COMPLIANT - Not a developer environment")
        return "COMPLIANT"

    # Check if the Lambda function's subnet IDs and security group match the desired values
    if security_group_id in SG_SUBNETS and set(subnet_ids).issubset(SG_SUBNETS[security_group_id]) and len(subnet_ids) == len(SG_SUBNETS[security_group_id]):
        print(f"✅ {resource_name} COMPLIANT - Valid network configuration")
        compliance_status = "COMPLIANT"
    else:
        print(f"⛔ {resource_name} NOT COMPLIANT - Incorrect network configuration")
        compliance_status = "NON_COMPLIANT"
    
    return compliance_status

def lambda_handler(event, context):
    # print(f"Received event: {event}")

    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event.get('configurationItem')

    print(f"Received configuration change for: ", configuration_item['resourceName'])
    # print(f"Configuration Item: {json.dumps(configuration_item)}")

    compliance_status = evaluate_compliance(configuration_item)

    # Get the current timestamp in ISO 8601 format
    current_timestamp = datetime.datetime.now().isoformat()

    # Report compliance status back to AWS Config
    config = boto3.client('config')
    result = config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': configuration_item['resourceType'],
                'ComplianceResourceId': configuration_item['resourceId'],
                'ComplianceType': compliance_status,
                'Annotation': 'Lambda function is not in the shared Security Group and Subnets configuration',
                'OrderingTimestamp': current_timestamp
            },
        ],
        ResultToken=event['resultToken']
    )

    #print(f"Config Result: {result}")
    print(f"Evaluated Compliance Status: {compliance_status}")

    return {
        'statusCode': 200,
        'body': json.dumps('Evaluation completed.')
    }
