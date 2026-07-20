#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = ["boto3>=1.43.51"]
# ///
"""Generate a long-lived API key tied to a Cognito/Gatekeeper user.

The "key" is a JSON object containing a Cognito refresh token alongside the
metadata needed to exchange it for a short-lived access token.  Refresh tokens
issued by the api-keys client are valid for 10 years.

Usage:
    python scripts/generate_api_key.py \\
        --username user@example.com \\
        --password "UserPassword1!" \\
        --client-id <statistician_api_keys_client_id> \\
        --user-pool-id <gatekeeper_user_pool_id> \\
        [--region us-east-1]

Outputs a JSON object to stdout.  Store it somewhere safe (e.g. a password
manager or Secrets Manager).  The key never expires unless you revoke it in
Cognito or rotate it by running this script again.

To use the key, exchange the refresh token for a short-lived access token:

    import boto3, json

    key = json.loads(open("api_key.json").read())
    client = boto3.client("cognito-idp", region_name=key["region"])
    resp = client.initiate_auth(
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": key["refresh_token"]},
        ClientId=key["client_id"],
    )
    access_token = resp["AuthenticationResult"]["AccessToken"]
    # Pass as:  Authorization: Bearer <access_token>
"""

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a long-lived Statistician API key for a Cognito user."
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Cognito username (email address) of the user to tie this key to.",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password for the Cognito user.",
    )
    parser.add_argument(
        "--client-id",
        required=True,
        help="Cognito app client ID (statistician_api_keys_client_id from Gatekeeper outputs).",
    )
    parser.add_argument(
        "--user-pool-id",
        required=True,
        help="Cognito user pool ID (user_pool_id from Gatekeeper outputs).",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1).",
    )
    args = parser.parse_args()

    import boto3
    from botocore.exceptions import ClientError

    cognito = boto3.client("cognito-idp", region_name=args.region)

    try:
        resp = cognito.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": args.username,
                "PASSWORD": args.password,
            },
            ClientId=args.client_id,
        )
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        print(f"Error authenticating with Cognito ({code}): {msg}", file=sys.stderr)
        sys.exit(1)

    if "ChallengeName" in resp:
        # The user has a pending auth challenge (e.g. NEW_PASSWORD_REQUIRED).
        print(
            f"Error: Cognito returned an auth challenge ({resp['ChallengeName']}) "
            "that must be resolved before an API key can be generated. "
            "Log in interactively first to complete any required setup steps.",
            file=sys.stderr,
        )
        sys.exit(1)

    refresh_token = resp["AuthenticationResult"]["RefreshToken"]

    api_key = {
        "username": args.username,
        "user_pool_id": args.user_pool_id,
        "client_id": args.client_id,
        "region": args.region,
        "refresh_token": refresh_token,
    }

    print(json.dumps(api_key, indent=2))
    print(
        "\nAPI key generated successfully. Store the JSON above somewhere safe.\n"
        "The refresh token is valid for 10 years and grants access to all private\n"
        "Statistician API routes as this user. Revoke it in Cognito if compromised.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
