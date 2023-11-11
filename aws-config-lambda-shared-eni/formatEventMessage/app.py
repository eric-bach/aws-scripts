import json
import boto3
import os

sns = boto3.client('sns')

def lambda_handler(event, context):
    #print(f"Event Received: {event}")

    detailType = event["detail-type"]   # Config Rules Compliance Change
    
    # AWS Config - Config Rules Compliance Change
    if (detailType == "Config Rules Compliance Change"):
        resourceId = event["detail"]["resourceId"]
        complianceType = event["detail"]["newEvaluationResult"]["complianceType"]
        annotation = event["detail"]["newEvaluationResult"]["annotation"]
        configRuleName = event["detail"]["configRuleName"]
        
        message = "ALERT! %s is %s\nAnnotation: %s\n\nRule: %s" % (resourceId, complianceType, annotation, configRuleName)

    # If the event doesn't match any of the above, return the event    
    else:
        message = str(event)
    
    sns.publish(
        TopicArn = os.environ['SNS_TOPIC_ARN'],
        Message = message
    )

    return {
      'statusCode': 200,
      'body': json.dumps('Success')
}