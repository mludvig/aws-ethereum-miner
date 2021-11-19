#!/bin/bash

if [ "$1" == "" ]; then
  echo "Usage: $0 {g4dn/g5/p3/p3dn/p4d} [vCPU]" >&2
  exit 1
fi

INST_TYPE=${1}
NUM_REGIONS=$(wc -l < regions-${INST_TYPE}.txt)

echo "Going to request Spot limit vCPU increase for ${INST_TYPE} to ${VCPU} in ${NUM_REGIONS} regions"

case "${INST_TYPE:0:1}" in
  g)
    Q_CODE="L-3819A6DF" # All G and VT Spot Instance Requests
    Q_VALUE=192
    ;;
  p)
    Q_CODE="L-7212CCBC" # All P Spot Instance Requests
    Q_VALUE=192
    ;;
  *)
    echo "Unknown instance type: ${INST_TYPE}" >&2
    exit 1
esac

VCPU=${2:-${Q_VALUE}}

for REGION in $(cat regions-${INST_TYPE}.txt); do
  echo -n "$(printf %20s ${REGION}) -- Current: "
  CURR=$(aws --region ${REGION} service-quotas get-service-quota --service-code ec2 --quota-code L-7212CCBC --query "Quota.Value" --output text)
  CURR=${CURR%.0} # Strip trailing .0
  echo -n "${CURR} "
  if [ "${CURR}" -lt "${VCPU}" ]; then
    echo "Increasing to: ${VCPU} "
  else
    echo "Ok"
  fi
done
