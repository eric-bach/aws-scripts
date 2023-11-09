# AWS State Manager - Start Stop Aurora Cluster by Tags

This creates a AWS State Manager Association that executes a AWS SSM Document to Start or Stop Aurora Clusters by Tags on a schedule

## Getting Started

1. Build the application

   ```
   $ sam build
   ```

2. Deploy the application

   ```
   $ sam deploy --profile AWS_PROFILE
   ```

3. Edit each of the Start and Stop Associations created in AWS State Manager
   a. Change the Execution from `Rate control` to `Simple execution`. CloudFormation currently only supports `Rate control`.
   b. Set the Input parameters
   AssumeRoleArn: ssm-automation-role
   Action: Start or Stop (to match the Association)
   TagKey: (the tag key to use)
   TagValue: (the tag value to use)

   TBA Screenshot
