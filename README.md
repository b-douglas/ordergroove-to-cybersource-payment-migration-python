#OrderGroove Credit Card Migration to Cybersource Token



## Overview

The Client has the requirement that **existing** Order Groove subscriptions must be migrated to use CyberSource payment tokens. The Client must retokenize the payment records that are stored for **existing** subscriptions.  Today, these payments are stored as encrypted AES in the OrderGrove system.  That means that they are stored inside the Order Groove system.   To migrate this payment information, a **The Client employee** will be required to migrate this data on behalf of The Client's consumers.

## Scripts
* [src/decodeOrderGroove.py]
Script was created to decrypt credit card info from OrderGroove
and then create file to be sent to CyberSource for processing
* [src/encodeOrderGroove.py]
Script was created to encode the CyberSource output file to be processed by OrderGrove file format.


## Documentation
Please read the attached techspec to get more details on the design.
* [Techspec.md]: 

  

