# AWS Ethereum miner

CloudFormation template for mining Ethereum (ETH) crypto currency on AWS GPU-enabled EC2 instances

<img align="right" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/128px-Ethereum_logo_2014.svg.png"/>

## Important!

- Read about the profitability on AWS mining in my article [Mining Bitcoin and other crypto on 
AWS](https://michael-ludvig.medium.com/mining-bitcoin-and-other-crypto-on-aws-eb172940059f) first!

- [Reach out to me](../../issues) if you need help with any customisation, e.g. to add support for other crypto currencies, etc.

## Quick start

1. Login to your AWS account and have your Ethereum wallet address ready
2. Click [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth.yml) (defaults to Ohio - us-east-2)
3. You will have an opportunity to check the stack details, enter the wallet address, etc, before the stack is launched.

## What does the template do?

* Spins up an AutoScaling Group with *Spot Instances* of the specified type (by default g4dn.xlarge)
* Runs ethminer with the right options upon the instance start

## Tell me more ...

Check out the instructions in my [Medium article](https://michael-ludvig.medium.com/mining-bitcoin-and-other-crypto-on-aws-eb172940059f),
it contains some important considerations. Alternatively, if you think you know what you are doing follow these instructions:

* Have your Ethereum wallet address ready. You can create a free one for example with [Guarda](https://guarda.io) if needed.
* Have an [AWS account](https://aws.amazon.com) ready.
* Click [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=ethminer&templateURL=https://s3.us-west-2.amazonaws.com/cnl4uehyq6/ethminer/template-eth.yml) (defaults to Ohio - us-east-2), enter the parameters and launch the stack.
* Check your mining progress on [Ethermine dashboard](https://ethermine.org/). 
  * Note that it takes some time (15 ~ 30 mins) before your stats start to appear, and 
  * The *reported* hashrate speed ramps up slowly to the sustained rate over the first hour or
    so, I believe due to delays in reporting and some averaging. 
  * From my tests the hashrate reported by the `ethminer` process is correct and that's what you get paid out. Even if the dashboard speed is lower.
* When done delete the stack.

## Author

Michael Ludvig, you're welcome :)
