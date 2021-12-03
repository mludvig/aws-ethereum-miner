#!/usr/bin/env python3

# CFN Custom Resource -- Filter the requested instance types
# InstanceTypesAttributes are filtered against InstanceTypesWanted
# and then against the instance types available in the current region

# Author: Michael Ludvig -- https://github.com/mludvig/aws-ethereum-miner

import json
import boto3
import urllib3

http = urllib3.PoolManager()
ec2 = boto3.client("ec2")

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


def filter_wanted(types, wanted):
    ## Wildcard -> return the full list
    if wanted == "*":
        print(f"Instance types wanted: * (=any)")
        return True, types

    ## Split and normalise the wanted list
    # Remove trailing wildcard and lowercase
    wanted_types = list(map(lambda x: x.strip().rstrip("*").lower(), wanted.split(",")))
    # Append "dot" if there's none, e.g. "g4dn" -> "g4dn."
    wanted_types = list(map(lambda x: x if x.find(".") >= 0 else f"{x}.", wanted_types))
    print(f"Instance types wanted: {' '.join(wanted_types)}")

    ## Filter the types against the wanted list
    filtered_types = []
    for wt in wanted_types:
        filtered_types.extend(list(filter(lambda x: x.startswith(wt), types)))
    filtered_types = list(set(filtered_types))  # Remove duplicates
    if not filtered_types:
        return False, "No wanted instance types match the available types."
    print(f"Instance types filtered: {' '.join(filtered_types)}")
    return True, filtered_types


def filter_available(types):
    result = ec2.describe_instance_type_offerings(
        LocationType="region", Filters=[{"Name": "instance-type", "Values": types}]
    )
    types_available = list(
        map(lambda x: x["InstanceType"], result["InstanceTypeOfferings"])
    )
    print(f"Instance types available in this region: {' '.join(types_available)}")
    return True, types_available


def lambda_handler(event, context):
    print("== EVENT ==")
    print(json.dumps(event))

    try:
        try:
            attrs = event["ResourceProperties"]["InstanceTypesAttributes"]
            wanted = event["ResourceProperties"]["InstanceTypesWanted"]
        except KeyError as e:
            raise Exception("Missing required property: {e}")

        try:
            # Extract the list of instance types - that's easier to match
            types = list(map(lambda x: x["InstanceType"], attrs))
        except KeyError as e:
            raise Exception(
                "'InstanceTypesAttributes' must be a list where each item must have an 'InstanceType' attribute"
            )

        ## Filter the 'types' list by 'wanted' instances
        success, types_wanted = filter_wanted(types, wanted)
        if not success:
            raise Exception(types_wanted)

        ## Filter the 'types' list by types available in this region
        success, types_available = filter_available(types_wanted)
        if not success:
            raise Exception(types_available)

        # Filter the new 'attrs' list from the filtered types
        attrs = list(filter(lambda x: x["InstanceType"] in types_available, attrs))
        if not attrs:
            raise Exception(
                "None of the requested instance types is available in this region!"
            )
    except Exception as e:
        send(event, context, FAILED, reason=f"Error: {e}")
        return False

    # Return the filtered list
    send(
        event,
        context,
        SUCCESS,
        {
            "InstanceTypeNames": ",".join(types_available),
            "InstanceTypeAttributes": attrs,
        },
    )
