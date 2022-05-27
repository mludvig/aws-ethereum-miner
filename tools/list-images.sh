#!/bin/bash

# Save the output of this script to ../src/ami-ids.yml

AMI_NAME_DL="Deep Learning AMI (Ubuntu 18.04) Version 60.2"
AMI_NAME_CUDA_X8664="ubuntu-22-04-nvidia-510-73-08-x8664 2022-05-26T06-25-07.884Z"
AMI_NAME_CUDA_ARM64="ubuntu-22-04-nvidia-510-73-08-aarch64 2022-05-26T06-25-02.812Z"
AMI_NAME_RADEON="ubuntu-20-radeon-21-40 2021-12-21T04-42-09.455Z"

AMI_OWNERS="amazon 769790836554"

REGIONS=$(aws ec2 describe-regions | jq -r '.Regions[].RegionName' | sort)

test -t 1 && cat << __EOF__
# CudaX8664: "${AMI_NAME_CUDA_X8664}"
# CudaARM64: "${AMI_NAME_CUDA_ARM64}"
# RadeonX8664: "${AMI_NAME_RADEON}"
# DeepLearning: "${AMI_NAME_DL}"
__EOF__

for REGION in ${REGIONS}; do
  AMI_JSON=$(aws --region ${REGION} ec2 describe-images --owners ${AMI_OWNERS} \
      --filters Name=name,Values="${AMI_NAME_DL}","${AMI_NAME_CUDA_X8664}","${AMI_NAME_CUDA_ARM64}","${AMI_NAME_RADEON}" 2>/dev/null)
  test -z "${AMI_JSON}" && continue

  echo "${REGION}:"
  echo -n "  CudaX8664: "; jq -r --arg name "${AMI_NAME_CUDA_X8664}" '.Images[]|select(.Name==$name).ImageId' <<< ${AMI_JSON}
  echo -n "  CudaARM64: "; jq -r --arg name "${AMI_NAME_CUDA_ARM64}" '.Images[]|select(.Name==$name).ImageId' <<< ${AMI_JSON}
  echo -n "  RadeonX8664: "; jq -r --arg name "${AMI_NAME_RADEON}" '.Images[]|select(.Name==$name).ImageId' <<< ${AMI_JSON}
  echo -n "  DeepLearning: "; jq -r --arg name "${AMI_NAME_DL}" '.Images[]|select(.Name==$name).ImageId' <<< ${AMI_JSON}
done

test -t 1 && echo "# Save the above output to ../src/ami-ids.yml"
