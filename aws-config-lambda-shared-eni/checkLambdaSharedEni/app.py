import datetime
import boto3
import json

def evaluate_compliance(configuration_item):
    # Define the desired subnet IDs and security group ID
    possible_subnet_ids = ["subnet-12345", "subnet-67890"]  # Replace with your desired subnet IDs
    possible_security_group_ids = ["sg-abcdefg"]  # Replace with your desired security group ID
    
    # Check if the Lambda function's subnet IDs and security group match the desired values
    subnet_ids = configuration_item.get("subnetIds", [])
    security_group_ids = configuration_item.get("securityGroupIds", [])
    
    if set(subnet_ids).issubset(possible_subnet_ids) and len(subnet_ids) == 4 and set(security_group_ids).issubset(possible_security_group_ids) and len(security_group_ids) == 1:
        compliance_status = "COMPLIANT"
    else:
        compliance_status = "NON_COMPLIANT"
    
    return compliance_status

# def evaluate_compliance(configuration_item):
#     # Your custom compliance evaluation logic goes here
#     # Example: Check if a Lambda function has a specific tag
#     if "tags" in configuration_item and "application" in configuration_item["tags"]:
#         compliance_status = "COMPLIANT"
#     else:
#         compliance_status = "NON_COMPLIANT"
    
#     return compliance_status

def lambda_handler(event, context):
    print("Event Received:", event)

    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event.get('configurationItem')

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
                'Annotation': 'Your custom annotation',
                'OrderingTimestamp': current_timestamp
            },
        ],
        ResultToken=event['resultToken']
    )

    print('Config Result: ', result)
    print('ResourceId: ', configuration_item['resourceId'])
    print('ComplianceStatus: ', compliance_status)

    return {
        'statusCode': 200,
        'body': json.dumps('Evaluation completed.')
    }