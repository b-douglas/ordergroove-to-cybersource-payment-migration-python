#OrderGroove Credit Card Migration to Cybersource Token



## Overview

The Client has the requirement that **existing** Order Groove subscriptions must be migrated to use CyberSource payment tokens. The Client must retokenize the payment records that are stored for **existing** subscriptions.  Today, these payments are stored as encrypted AES in the OrderGrove system.  That means that they are stored inside the Order Groove system.   To migrate this payment information, a **The Client employee** will be required to migrate this data on behalf of The Client's consumers.

## Assumptions

- Order Groove cannot migrate this data on The Client's behalf because they do not have access to CyberSource
- OrderGroove should be able to reduce the migrations by purging dormant subscriptions in the system
- A Client employee would be tasked to migrate more than 10,,000 active subscriptions.
- This activity would occur one time during the cutover to use of CyberSource payment tokens.

## Design Detail

The following steps will need to occur:

1. Order Groove will place a CSV file that includes all payments to be migrated
2. The Client Employee will download the CSV to their secure VM
3. Employee will run the script to decrypt Credit Card numbers
       For each row in CSV
   1. Decrypt AES Encrypted CC Number
   2. Write Record to Output file
      Columns are: {OGCustomerId, SubscriptionId, CyberSource Token}
4. Employee will upload unencrypted CSV file to CyberSource portal for tokenization
   1. Tokenization could take up to ~1 hour?
5. Employee downloads the CyberSource results from the portal
   1. Note: it is unknown at this time what the CyberSource results will be.  If they match the format we give it.  If not we would need an additional script to retranslate the CyberSource token into the order grove CSV file format. Please see output CSV format below
6. Employee uploads the Order Groove CSV with  Tokens
   1. Note: Assume we may need an additional script to aggregate what comes from CyberSource and replaces the AES CC num from the original file.

### Additional Requirements:

- Python script must translate into the CyberSource Bulk upload format
  - The script must output only unique CC Numbers to prevent duplicate records
- May need an additional script to re-translate into the Order Groove CSV file format - Please see output CSV format below
- Order Groove mandates only one Cybersource Token per OG Customer ID

### Incoming CSV File Format

- Subscription Status
- Next Order
- Date Originating Order ID
- Merchant Customer ID
- User Token ID
- **OG Customer ID**
- Email Address
- First Name
- Last Name
- Product
- Product ID
- SKU
- Attribute
- Frequency Days
- Frequency Every
- Frequency Period
- Quantity
- Token ID
- **CC Holder  -  AES encrypted**
- **CC Number  -  AES encrypted**
- **CC Type -  AES encrypted**
- **CC Expiration Date -  AES encrypted**
- Billing First
- Billing Last
- Billing Address 1
- Billing Address 2
- Billing City
- Billing State
- Billing Zip
- Billing Company
- Billing Country
- Billing Phone
- Billing Fax
- Shipping First
- Shipping Last
- Shipping Address 1
- Shipping Address 2
- Shipping City
- Shipping State
- Shipping Zip
- Shipping Company
- Shipping Country
- Shipping Phone
- Shipping Fax
- Subscription Start Date
- Subscription Create Date
- Order Counter
- Public Offer ID
- Subscription Extra Data
- **Subscription ID**

### Output CSV File Format

- **OG Customer ID**
- **Subscription ID  (May not be needed)**
- **CyberSource Token**
- **CC Type -  AES encrypted**
- **CC Expiration Date -  AES encrypted**

### AES Decryption

For the CC decryption - the file will use the AES encrypted version of the credit card numbers, the same way we provide the data in the order XML we send to Salesforce today. I think you mentioned Python (correct me if I'm wrong) - 

This is an example we've shared with other merchants in the past on AES encryption with Python, as it would be similarly decrypted:
 

### CyberSource Tokenization

We had looked at using the CyberSource SOAP toolkit; however, it was felt this was too complex to setup.

Instead, we will use the manual approach.  


For the manual approach, we will use upload a CSV or list of Credit Card numbers, and then the bulk processing will return us back a list of CyberSource Tokens.

####  CyberSource Manual Steps

- Enter your merchantID and email

- The batchID needs to be unique per batch (Format: alphanumeric with a maximum of 8 characters)

- Excel will truncate anything over 15 digits, you will need to format the cells as text

- When you make updates to the file you will either need to open it in a text editor or import it as text in excel to prevent the values from being truncated

- Test with a few transactions first to make sure the data is being entered correctly

- The recordCount will need to be entered and SUM=0 will remain static since there aren’t amounts

Provided are the steps to upload the batch file in the Business Center:

1. Log into the Business Center,

·     Production: [https://ebc.cybersource.com/ebc2/](https://protect-us.mimecast.com/s/Uz7nCDkxWwi5DZRqpUAoA18?domain=ebc.cybersource.com/)

·     Test: [https://ebctest.cybersource.com/ebc2](https://protect-us.mimecast.com/s/kZ81CERyWKT3kjQLyiPXylM?domain=ebctest.cybersource.com)

1. Select Virtual Terminal > Batch Transaction Upload > BATCH UPLOAD > BROWSE the file > SAVE


This is also explained starting on page 11 of the provided documentation:

[http://apps.cybersource.com/library/documentation/dev_guides/Offline_Trans_File_Submission/Batch_Upload_ENT.pdf](https://protect-us.mimecast.com/s/a7kRCG6AWwh129Vkntkck0w?domain=apps.cybersource.com)

 

The batch file is placed in a queue to be processed. An email will be sent confirming if the file is validated successfully. If validated successfully it will be processed and response files will be generated. A reply.all file which shows all transactions and reply.rejected file which shows transaction that weren’t processed successfully. The report is available in the Business Center by selecting Reports > Available Reports under Downloadable Report > Third-Party Reports.



## Security

- Workspaces should be deployed in a private VPC with a NAT gateway. The NAT should be restricted as much as possible. https://docs.aws.amazon.com/workspaces/latest/adminguide/amazon-workspaces-vpc.html#configure-vpc-nat-gateway
- Restrict workspaces access to a trusted device ie whichever device will be utilized to access workspaces https://docs.aws.amazon.com/workspaces/latest/adminguide/trusted-devices.html
- Web access should be disabled
- Encrypt Workspaces using KMS or better

## Infrastructure

Process script will be run from an Amazon Workspace that is PCI compliant and only allows a specific The Client Employee to do., and connect to the Order Groove SFTP and the CyberSource Payment Gateway. 