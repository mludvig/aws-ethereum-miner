#!/usr/bin/env python3

# CFN Custom Resource -- Filter the requested instance types
# InstanceTypesAttributes are filtered against InstanceTypesWanted
# and then against the instance types available in the current region

# Author: Michael Ludvig -- https://github.com/mludvig/aws-ethereum-miner

import os
import json
import urllib3
import datetime
import boto3

http = urllib3.PoolManager()
ec2 = boto3.client("ec2")

# Little usability hack:
# IF $VPC_ID is not specified (= template-eth-default-vpc.yml)
# AND the account supports EC2-Classic (instance product name ends with "Amazon VPC")
# THEN we have to advise the user to use "template-eth-custom-vpc.yml" instead.
VPC_ID = os.getenv("VPC_ID")

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
    wanted_list = list(map(lambda x: x.strip().rstrip("*").lower(), wanted.split(",")))
    # Append "dot" if there's none, e.g. "g4dn" -> "g4dn."
    wanted_list = list(map(lambda x: x if x.find(".") >= 0 else f"{x}.", wanted_list))
    # Find unwanted types (prepended with "-")
    unwanted_list = list(filter(lambda x: x.startswith('-'), wanted_list))
    # Remove unwanted from wanted
    wanted_list = [ wt for wt in wanted_list if wt not in unwanted_list ]
    # Strip leading "-" from unwanted_list
    unwanted_list = [ ut[1:] for ut in unwanted_list ]
    print(f"Instance types wanted: {' '.join(wanted_list)} / unwanted: {' '.join(unwanted_list)}")

    # Remove unwanted types
    unwanted_types = []
    for ut in unwanted_list:
        unwanted_types.extend(list(filter(lambda x: x.startswith(ut), types)))
    unwanted_types = set(unwanted_types)
    types = list(set(types).difference(unwanted_types))

    # If the user only specified unwanted types ...
    if not wanted_list or wanted_list == "*":
        print(f"Instance types filtered: {' '.join(types)}")
        return True, types

    ## Filter the types against the wanted list
    filtered_types = []
    for wt in wanted_list:
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


def sort_by_efficiency(attrs):
    data = {t["InstanceType"]: t for t in attrs}

    # Retrieve current spot prices
    result = ec2.describe_spot_price_history(
        InstanceTypes=list(data.keys()),
        ProductDescriptions=["Linux/UNIX", "Linux/UNIX (Amazon VPC)"],
        StartTime=datetime.datetime.now() - datetime.timedelta(minutes=1),
    )

    # Calculate average spot price for each instance
    for r in result["SpotPriceHistory"]:
        if not VPC_ID and r["ProductDescription"].endswith("(Amazon VPC)"):
            raise Exception(
                'Your account still supports EC2-Classic. Please deploy "template-eth-custom-vpc.yml" instead.'
            )
        t = r["InstanceType"]
        if "_count" not in data[t]:
            data[t]["_count"] = 0
            data[t]["_sum"] = 0.0
        data[t]["_count"] += 1
        data[t]["_sum"] += float(r["SpotPrice"])

    # Calculate efficiency (Hashrate per spot price)
    for t in data.keys():
        data[t]["_spot"] = data[t]["_sum"] / data[t]["_count"]
        data[t]["_efficiency"] = (
            float(data[t].get("WeightedCapacity", 1)) / data[t]["_spot"]
        )
        del data[t]["_sum"]
        del data[t]["_count"]

    # Sort by efficiency
    attrs = list(data.values())
    attrs.sort(key=lambda x: (-x["_efficiency"], x["_spot"]))

    print(f"Instances sorted: {json.dumps(attrs)}")

    # Remove _* fields
    for a in attrs:
        for key in list(a.keys()):
            if key.startswith("_"):
                del a[key]

    return attrs


def lambda_handler(event, context):
    print("== EVENT ==")
    print(json.dumps(event))

    if event["RequestType"] == "Delete":
        send(event, context, SUCCESS)
        return

    try:
        try:
            attrs = event["ResourceProperties"]["InstanceTypesAttributes"]
            wanted = event["ResourceProperties"]["InstanceTypesWanted"]
            region = event["ServiceToken"].split(":")[3]
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
        print(
            f"Excluded in {region} region:",
            json.dumps(
                [
                    x["InstanceType"]
                    for x in attrs
                    if region in x.get("_ExcludeInRegions", [])
                ]
            ),
        )
        attrs = list(
            filter(
                lambda x: x["InstanceType"] in types_available
                and region not in x.get("_ExcludeInRegions", []),
                attrs,
            )
        )
        if not attrs:
            raise Exception(
                "None of the requested instance types is available in this region!"
            )

        # Calculate efficiency (Hashrate per spot USD)
        attrs = sort_by_efficiency(attrs)
        types_sorted = list(map(lambda x: x["InstanceType"], attrs))

    except Exception as e:
        send(event, context, FAILED, reason=f"Error: {e}")
        return False

    # Return the filtered list
    send(
        event,
        context,
        SUCCESS,
        {
            "InstanceTypeNames": " ".join(types_sorted),
            "InstanceTypeAttributes": attrs,
        },
    )
