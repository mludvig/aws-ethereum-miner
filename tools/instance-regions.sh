#!/bin/bash -e

# Find the regions where the given instance types are available

INSTANCES="p3dn.24xlarge p3.2xlarge g4dn.xlarge g5.xlarge p4d.24xlarge"

REGIONS=$(aws ec2 describe-regions | jq -r '.Regions[].RegionName' | sort)

for REGION in ${REGIONS}; do
  echo "=== Region: ${REGION}" >&2
  # Instance availability
  aws --region ${REGION} ec2 describe-instance-type-offerings --location-type "region" --filters Name=instance-type,Values=${INSTANCES// /,} | jq -c .InstanceTypeOfferings
done > instance-regions.json

echo

for INSTANCE in ${INSTANCES}; do
  FILE=regions-${INSTANCE%.*}.txt
  echo "--- ${FILE}"
  grep ${INSTANCE} instance-regions.json | jq -r '.[0].Location' > ${FILE}
done

rm -f instance-regions.json
