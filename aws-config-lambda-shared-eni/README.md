# AWS Config - Lambda Shared ENI

This creates an AWS Config Custom Rule that checks to ensure Lambda functions are created in the predefined Security Group and Subnet combination.

Requires AWS Config enabled to record configuration changes to at a minimum Lambda function resource types.

When a Lambda function is not configured correctly an email message is sent to notify about the mis-configuration.

## Getting Started

1. Build the application

   ```
   $ sam build
   ```

2. Deploy the application

   ```
   $ sam deploy --parameter-overrides EmailAddress=EMAIL_ADDRESS --profile AWS_PROFILE
   ```
