# Statistician

**Statistician** is an overcomplicated way for me to manage and publish fun facts and statistics about my life.
It's built on Amazon Web Services, with the primary goal to serve the fun facts feature of [my personal website](https://bensoyka.com).

## Project structure

There are a few components to make Statistician work:

- `funcs/`: Lambda function handlers to respond to HTTP requests to the API.
- `infra/`: Terraform configuration to provision the AWS resources.

This is a bare-bones starter setup, with more features yet to be built.
See what's coming on [the issue tracker](https://github.com/bsoyka/statistician/issues).

## AWS resources

Several [AWS](https://aws.amazon.com/) technologies are used to power Statistician:

- Lambda: Serverless compute service that runs code in response to events.
- API Gateway: Manages HTTP requests and routes them to the appropriate Lambda functions.
- DynamoDB: NoSQL database service that stores the fun facts and statistics.
- Cognito: Identity and access management service, set up through a different personal project called [Gatekeeper](https://github.com/bsoyka/gatekeeper).

These are all provisioned using [Terraform](https://developer.hashicorp.com/terraform).
