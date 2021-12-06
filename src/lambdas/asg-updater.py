#!/usr/bin/env python3

# CFN Custom Resource -- ASG Updater
# Set the ASG Desired Capacity _after_ the ASG has been
# created with DC=0 to speed up its creation in CFN.
# The Custom Resource requires 2 parameters:
# - AsgName
# - DesiredCapacity

# Author: Michael Ludvig -- https://github.com/mludvig/aws-ethereum-miner

import json
import boto3
import urllib3

http = urllib3.PoolManager()
asg = boto3.client("autoscaling")
SUCCESS = "SUCCESS"
FAILED = "FAILED"


def send(event, context, status, data={}, reason=None):
    responseUrl = event["ResponseURL"]
    responseBody = {
        "Status": status,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Reason": reason
        or "See the details in CloudWatch Log Stream: {}".format(
            context.log_stream_name
        ),
    }
    if data:
        responseBody["Data"] = data
    json_responseBody = json.dumps(responseBody)
    print("== RESPONSE ==")
    print(json_responseBody)
    headers = {"content-type": "", "content-length": str(len(json_responseBody))}
    try:
        response = http.request(
            "PUT", responseUrl, headers=headers, body=json_responseBody
        )
        print("Status code:", response.status)
    except Exception as e:
        print("send(..) failed executing http.request(..):", e)


def lambda_handler(event, context):
    print("== EVENT ==")
    print(json.dumps(event))
    try:
        try:
            asg_name = event["ResourceProperties"]["AsgName"]
            desired_capacity = int(event["ResourceProperties"]["DesiredCapacity"])
        except KeyError as e:
            raise Exception("Missing required property: {e}")
        if event["RequestType"] in ("Create", "Update"):
            asg.set_desired_capacity(
                AutoScalingGroupName=asg_name, DesiredCapacity=desired_capacity
            )
            print(f"Setting desired capacity for '{asg_name}' to {desired_capacity}")
    except Exception as e:
        send(event, context, FAILED, reason=f"Error: {e}")
        return False
    send(
        event,
        context,
        SUCCESS,
        {"DesiredCapacity": desired_capacity},
    )
