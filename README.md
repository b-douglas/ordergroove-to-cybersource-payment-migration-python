# OrderGroove Credit Card Migration to Cybersource Token

## Overview

This repo is a collection of python scripts that can be used to migrate **existing** Order Groove subscriptions to use CyberSource payment tokens. For old OrderGroove customers, payments are stored as encrypted AES in the database system.  Migrating the credit card numbers ensures a higher security level by only keeping the CyberSource Payment Tokens.

## Scripts
These are the main scripts.
* [src/decodeOrderGroove.py](src/decodeOrderGroove.py)
The script was created to decrypt credit card info from OrderGroove
and then make the file to be sent to CyberSource for processing
* [src/encodeOrderGroove.py](src/encodeOrderGroove.py)
The script was created to encode the CyberSource output file to be processed by OrderGrove file format.
* [src/config.ini.template](src/config.ini.template)
A sample config.ini file that contains the options needed for each python script. **ALL** python scripts use the same `.ini` file for all.


## Miscellaneous Scripts
Here are some additional scripts I had to write to diagnose the issues I had with the process.
* [misc/decodeOrderGroove-stripOutOld.py](misc/decodeOrderGroove-stripOutOld.py)
The script is similar to the decrypt credit card; however, it adds a dictionary to strip out existing or duplicate records.
* [misc/extractIdsNoCreditCards.py](misc/extractIdsNoCreditCards.py)
The script is similar to the decodeOrderGrove, except it does not decrypt the credit card numbers.  I needed that to get a list of subscription ids.

## Combine Scripts
For another site, I already had the Cybersource Token, so this python just combines what I get from Order Groove.
* [combine/combineOrderGrooveATG.py](combine/combineOrderGrooveATG.py)

## Documentation
Please read the attached tech-spec to get more details on the design.
* [techspec.md](techspec.md)
