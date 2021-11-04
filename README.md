# AWS Ethereum miner

CloudFormation template for mining Ethereum (ETH) crypto currency on AWS GPU-enabled EC2 instances

<img align="right" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/128px-Ethereum_logo_2014.svg.png"/>

## Important!

- Read about the profitability on AWS mining in my article [Mining Bitcoin and other crypto on 
AWS](https://michael-ludvig.medium.com/mining-bitcoin-and-other-crypto-on-aws-eb172940059f) first!

- [Reach out to me](../../issues) if you need help with any customisation, e.g. to add support for other crypto currencies, etc.

## Quick start

1. Login to your AWS account and have your Ethereum wallet address ready
2. Launch the stack in one or more of the cheapest regions. Sometimes spot capacity is not available in a particular region, in that case try a different one.
  * **Oregon** _us-west-2_ [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth-default-vpc.yml)
  * **Ohio** _us-east-2_ [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth-default-vpc.yml)
  * **N. Virginia** _us-east-1_ [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth-default-vpc.yml)

You will have an opportunity to check the stack details, enter the wallet address, etc, before the stack is launched.

### What does the template do?

* Spins up an AutoScaling Group with *Spot Instances* of the specified type (by default _g4dn.xlarge_)
  * Use [template-eth-default-vpc.yml](template-eth-default-vpc.yml) if you want to spin up the instances in the _Default VPC_ (most users).
  * Use [template-eth.yml](template-eth.yml) if you have _your own VPC_ that you want to use (advanced users). 
    The Subnets must have direct or NAT access to the internet! Make sure that the VPC matches the Subnets selected!!
* Runs `ethminer` with the right options upon the instance start

### Increase resource quotas

AWS accounts have default limits (quotas) on some resources. You may find, for example, that your quota for 
_All G and VT Spot Instance Requests_ in a particular region is *0* and you therefore can't start any `g4dn.xlarge` instances.
It pays to request the quotas increase which can be done with this simple command (you can do this from the CloudShell):

```
export AWS_REGION=us-west-2 # Oregon
export CODE=L-3819A6DF      # All G and VT Spot Instance Requests (for g4dn.xlarge, etc)
# export CODE=L-7212CCBC    # All P Spot Instance Requests (for p3.2xlarge, p3dn.24xlarge or p4d.24xlarge)
export VCPUS=96             # 96 vCPUs - can accommodate e.g. 24x g4dn.xlarge or 1x p4d.24xlarge

aws --region ${REGION} service-quotas request-service-quota-increase --service-code ec2 --quota-code ${CODE} --desired-value ${VCPUS}
```

Choose the number of *vCPU* and the *Quota code* according to your needs.

### Expand to Los Angeles (us-west-2-lax-1)

Spot instance capacity for `g4dn.xlarge` instances is in short supply in the cheapest regions, even though the spot 
prices are still very very low. You may have to wait for a long time to get an instance.

Interestingly the *Los Angeles local zone* seems to have plenty of g4dn spot capacity at the same price as Oregon, 
however you have to opt-in to be able to use it. Here is how (you can do this from the CloudShell):

1. **Opt-in to the LAX zone** with: 
    ```
    aws --region us-west-2 ec2 modify-availability-zone-group --group-name us-west-2-lax-1 --opt-in-status opted-in
    ```
2. Create new **default subnets** in the 2 LAX AZs in the default Oregon VPC:
    ```
    aws --region us-west-2 ec2 create-default-subnet --availability-zone us-west-2-lax-1a
    aws --region us-west-2 ec2 create-default-subnet --availability-zone us-west-2-lax-1b
    ```
3. **Delete and re-deploy** the CFN stack in **us-west-2 (Oregon)** - it will pick up the 2 new AZs and launch the instances.

## Tell me more ...

Check out the instructions in my [Medium article](https://michael-ludvig.medium.com/mining-bitcoin-and-other-crypto-on-aws-eb172940059f),
it contains some important considerations. Alternatively, if you think you know what you are doing follow these instructions:

* Have your Ethereum wallet address ready. You can create a free one for example with [Guarda](https://guarda.io) if needed.
* Login to your [AWS account](https://aws.amazon.com).
* Click the [Launch link](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth-default-vpc.yml) or create the stack manually:
  * Download the [template-eth.yml](template-eth.yml) template or [template-eth-default-vpc.yml](template-eth-default-vpc.yml) or clone this Github repository.
  * In the AWS Console select one of the cheap regions (typically Oregon, N.Virginia, or Ohio)
  * Create a CloudFormation stack from the [template-eth-default-vpc.yml](template-eth-default-vpc.yml)
* Check your mining progress on [Ethermine dashboard](https://ethermine.org/). 
  * Note that it takes some time (15 ~ 30 mins) before your stats start to appear, and 
  * The *reported* hashrate speed ramps up slowly to the sustained rate over the first hour or
    so, I believe due to delays in reporting and some averaging. 
  * From my tests the hashrate reported by the `ethminer` process is correct and that's what you get paid out. Even if the dashboard speed is lower.
* When done delete the stack.

## Author

[Michael Ludvig](https://aws.nz), you're welcome :)

Did you make some profit using this template and wish to say thanks? Any ETH amount sent to my address will be much appreciated: **0x99b36B44cf319c9E0ed4619ee2050B21ECac2c15**

![0x99b36B44cf319c9E0ed4619ee2050B21ECac2c15](qr.png)

Thanks! :)
