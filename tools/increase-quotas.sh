#!/bin/bash

Q_VALUE=64

if [ "$1" == "" ]; then
  echo "Usage: $0 {g4dn/g5/p3/p3dn/p4d} [vCPU]" >&2
  echo ""
  echo -e "Unless \e[1mvCPU\e[0m parameter is used we will request increase to \e[1m${Q_VALUE}\e[0m vCPU"
  echo ""
  exit 1
fi

INST_TYPE=${1}

case "${INST_TYPE:0:1}" in
  g)
    Q_CODE_SPOT="L-3819A6DF" # All G and VT Spot Instance Requests
    Q_CODE_ONDE="L-DB2E81BA" # Running On-Demand G and VT instances
    ;;
  p)
    Q_CODE_SPOT="L-7212CCBC" # All P Spot Instance Requests
    Q_CODE_ONDE="L-417A185B" # Running On-Demand P instances
    ;;
  *)
    echo "Unknown instance type: ${INST_TYPE}" >&2
    exit 1
esac

VCPU=${2:-${Q_VALUE}}
NUM_REGIONS=$(wc -l < regions-${INST_TYPE}.txt)

echo
echo -e "\e[1mGoing to request Spot limit vCPU increase for ${INST_TYPE} to ${VCPU} in ${NUM_REGIONS} regions\e[0m"
echo

for REGION in $(cat regions-${INST_TYPE}.txt); do
  echo -n "$(printf %20s ${REGION}) -- Current: "
  CURR=$(aws --region ${REGION} service-quotas get-service-quota --service-code ec2 --quota-code ${Q_CODE_SPOT} --query "Quota.Value" --output text)
  CURR=${CURR%.0} # Strip trailing .0
  echo -n "${CURR} "
  if [ "${CURR}" -ge "${VCPU}" ]; then
    echo "Ok"
    continue
  fi
  echo "Increasing to: ${VCPU} "
  aws --region ${REGION} service-quotas request-service-quota-increase --service-code ec2 --quota-code ${Q_CODE_SPOT} --desired-value ${VCPU} > /dev/null
done

echo
echo -e "\e[1mGoing to request On-Demand limit vCPU increase for ${INST_TYPE} to ${VCPU} in ${NUM_REGIONS} regions\e[0m"
echo

for REGION in $(cat regions-${INST_TYPE}.txt); do
  echo -n "$(printf %20s ${REGION}) -- Current: "
  CURR=$(aws --region ${REGION} service-quotas get-service-quota --service-code ec2 --quota-code ${Q_CODE_ONDE} --query "Quota.Value" --output text)
  CURR=${CURR%.0} # Strip trailing .0
  echo -n "${CURR} "
  if [ "${CURR}" -ge "${VCPU}" ]; then
    echo "Ok"
    continue
  fi
  echo "Increasing to: ${VCPU} "
  aws --region ${REGION} service-quotas request-service-quota-increase --service-code ec2 --quota-code ${Q_CODE_ONDE} --desired-value ${VCPU} > /dev/null
done
