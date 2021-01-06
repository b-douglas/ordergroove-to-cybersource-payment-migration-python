#OrderGroove Credit Card Migration to Cybersource Token

## Overview

This repo is a collection of python scripts that can be used to migrate **existing** Order Groove subscriptions to use CyberSource payment tokens. For old Order Grove customers  payments are stored as encrypted AES in the database system.  To ensure higher security it make sense to move the CreditCard numbers to CyberSource and then be stored as CyberSource payment Tokens.

## Scripts
These are the main scripts.
* [src/decodeOrderGroove.py](src/decodeOrderGroove.py)
Script was created to decrypt credit card info from OrderGroove
and then create file to be sent to CyberSource for processing
* [src/encodeOrderGroove.py](src/encodeOrderGroove.py)
Script was created to encode the CyberSource output file to be processed by OrderGrove file format.
* [src/config.ini.template](src/config.ini.template)
A sample config.ini file that contains the options needed for each python script. **ALL** python scripts use the same `.ini` file for all.


## Miscalaneous Scripts
Here are some additional scripts I had to write to tweak diagnosis issues I had with the process.
* [misc/decodeOrderGroove-stripOutOld.py](src/decodeOrderGroove-stripOutOld.py)
Script is similar to the dectypt credit card however it adds a dictionary to strip out existing or duplicate records.
* [misc/extractIdsNoCreditCards.py](src/extractIdsNoCreditCards.py)
Script is similar to the decodeOrderGrove except it does not decrypt the credit card numbers.  I needed that to get a list of subscription ids

## Documentation
Please read the attached techspec to get more details on the design.
* [techspec.md](techspec.md)

  

