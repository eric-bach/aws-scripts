import datetime
import boto3
import json

def evaluate_compliance(configuration_item):
    # Your custom compliance evaluation logic goes here
    # Example: Check if a Lambda function has a specific tag
    compliance_status = "NON_COMPLIANT"

    return compliance_status

def lambda_handler(event, context):
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event.get('configurationItem')

    compliance_status = evaluate_compliance(configuration_item)

    # Get the current timestamp in ISO 8601 format
    current_timestamp = datetime.datetime.now().isoformat()

    # Report compliance status back to AWS Config
    config = boto3.client('config')
    config.put_evaluations(
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

    print('ResourceId: ', configuration_item['resourceId'])
    print('ComplianceStatus: ', compliance_status)

    return {
        'statusCode': 200,
        'body': json.dumps('Evaluation completed.')
    }