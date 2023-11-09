import datetime
import boto3
import json

F1_SG = "sg-0b4baaeedcc5c3dce"
M2_SG = "sg-01f3059a533b62208"
EXP_SG = "sg-06bc7733c60f6741e"
OMN_SG = "sg-06dcd4bc0a4eb5d7c"
SUBNET_1 = "subnet-0c97477b31b49f8be"
SUBNET_2 = "subnet-0351248ea92ee561e"
SUBNET_3 = "subnet-0f3dbaccd2c1fcf36"
SUBNET_4 = "subnet-0418853079ef7eb8a"
SG_SUBNETS = {
    F1_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4],
    M2_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4],
    EXP_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4],
    OMN_SG: [SUBNET_1, SUBNET_2, SUBNET_3, SUBNET_4]
}

def evaluate_compliance(configuration_item):
    # Check if the Lambda function's subnet IDs and security group match the desired values
    security_group_id = configuration_item.get("securityGroupIds", [])[0]
    subnet_ids = configuration_item.get("subnetIds", [])

    # TODO Check that this is a developer lambda

    if security_group_id in SG_SUBNETS and set(subnet_ids).issubset(SG_SUBNETS[security_group_id]) and len(subnet_ids) == 4:
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
