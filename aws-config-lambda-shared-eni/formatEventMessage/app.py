import json
import boto3
import os

sns = boto3.client('sns')

def lambda_handler(event, context):
    print("Event Received:", event)

    detailType = event["detail-type"]   # Config Rules Compliance Change
    region = event["region"]           
    accountId = event["account"]
    
    #Config Rules Compliance Change
    if (detailType == "Config Rules Compliance Change"):
            
        resourceId = event["detail"]["resourceId"]
        complianceType = event["detail"]["newEvaluationResult"]["complianceType"]

        configRuleName = event["detail"]["configRuleName"]
        
        message = "ALERT: %s is %s" % (resourceId, complianceType)

    #If the event doesn't match any of the above, return the event    
    else:
        message = str(event)
    
    response = sns.publish(
        TopicArn = os.environ['SNS_TOPIC_ARN'],
        Message = message
    )
    print("SNS Response:", response)

    return {
      'statusCode': 200,
      'body': json.dumps('Success!')
}