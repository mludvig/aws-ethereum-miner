#!/bin/bash

G_SPOT="L-3819A6DF"      # All G and VT Spot Instance Requests
G_ONDEMAND="L-DB2E81BA"  # Running On-Demand G and VT instances
P_SPOT="L-7212CCBC"      # All P Spot Instance Requests
P_ONDEMAND="L-417A185B"  # Running On-Demand P instances

function get_quota
{
  CURR=$(aws --region ${1} service-quotas get-service-quota --service-code ec2 --quota-code ${2} --query "Quota.Value" --output text)
  CURR=${CURR%.0} # Strip trailing .0
  echo ${CURR}
}

echo "Listing regions..."
REGIONS=$(aws --region us-east-1 ec2 describe-regions | jq -r '.Regions[].RegionName' | sort)

echo "               |  G4*/G5* types |  P3*/P4* types"
echo "Region         | OnDemand  Spot | OnDemand  Spot"
echo "---------------+----------------+---------------"
for REGION in ${REGIONS}; do
  printf "%-14s | " ${REGION}
  printf "%8d" $(get_quota ${REGION} ${G_ONDEMAND})
  printf "%6d | " $(get_quota ${REGION} ${G_SPOT})
  printf "%8d" $(get_quota ${REGION} ${P_ONDEMAND})
  printf "%6d" $(get_quota ${REGION} ${P_SPOT})
  echo
done
