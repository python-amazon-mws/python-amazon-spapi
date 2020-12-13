# python-amazon-spapi

Python toolkit for working with Amazon's Selling Partner API (SP-API)

This project is just a starter, with no usable code at the moment. If you wish to make your own client for the time being, please make use of [Amazon's SP-API Swagger models](https://github.com/amzn/selling-partner-api-models), as well as their [documentation](https://github.com/amzn/selling-partner-api-docs).

If you have a need to connect to Amazon seller services and can use MWS (legacy service), please have look at our other project, [python-amazon-mws][1].

[1]: https://github.com/python-amazon-mws/python-amazon-mws


Basic example for this fork:
Put all the creds in your env variables or the env file provided in .sellerpartnerapi.env.
```python
from spapi import main, setup

sts = setup.StsTokenRequest()
stscreds = sts.get_sts_creds()

at = setup.AccessTokenRequest()
access_token = at.get_access_token()

subpath = '/sellers/v1/marketplaceParticipations'

spapi = main.SPAPI(
    access_token=access_token, stscreds=stscreds,
    path=subpath, region='germany')

response = spapi.main()
response.json()
```