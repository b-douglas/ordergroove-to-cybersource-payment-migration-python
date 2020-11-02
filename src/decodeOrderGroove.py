#!/usr/bin/python
"""
Created on Oct 08, 2020

decodeOrderGroove.py

Script was created to decrypt credit card info
and then create file to be sent to OrderGroove for processing

@author: dougrob
"""

import configparser
import csv
# import os
# import re
import sys
import base64
from Crypto.Cipher import AES
import time


# ## Function to open a file as a csv
# ##  All of the files are treated as a Csv, whether they are true CSVs or not.
# ## The reason for this is so that if a file needs more columns we have that ability
def open_csv(fname, t="r", fieldnames=""):
    """ Function to open a csv file """
    fhand = open(fname, t)
    if t == "r":
        csvfile = csv.DictReader(fhand, dialect='excel')
    else:
        csvfile = csv.DictWriter(
            fhand, dialect='excel', quoting=csv.QUOTE_NONE, fieldnames=fieldnames)
    return csvfile


def trace(level, string):
    """ Trace function """
    if level <= int(config.get('Debug', 'LogLevel')):
        print('%s' % string)
        sys.stdout.flush()


def decodeCardType(string):
    """ Mapping function that converts card types into Cybersource numbers """
    cardtype = string.strip().lower()
    typecode = "-1"
    if cardtype == "visa":
        typecode = "001"
    elif cardtype == "mastercard" or cardtype == "eurocard":
        typecode = "002"
    elif cardtype == "american express":
        typecode = "003"
    elif cardtype == "discover":
        typecode = "004"
    elif cardtype == "diners club":
        typecode = "005"
    elif cardtype == "carte blanche":
        typecode = "006"
    elif cardtype == "jcb":
        typecode = "007"
    else:
        trace(1, "ERROR! Credit Card Type does not match!")
        raise ValueError("Credit Card Type does not match!")
    return typecode


def decodeCardExpDate(string):
    """ Function to strip and split month as a list"""
    try:
        l = string.strip().split("/")
        if len(l) == 2:
            return l
        raise ValueError("\'%s\' is an invalid month year." % string)
    except Exception as e:
        raise e


def decryptOrderGroove(cipher, encrypted_string):
    """ Function to decrypt data from OrderGroove using it's cipher """
    PADDING = '{'
    try:
        return cipher.decrypt(base64.b64decode(encrypted_string)).decode('ascii').rstrip(PADDING)
    except Exception as e:
        raise e


def formatCyberSourceCSVHeader(recordCount):
    """ Function to format the correct CSV Header that Cybersource expects for Batch Upload"""
    try:
        d = time.strftime("%Y-%m-%d")
        batchId = "%s%s" % (config.get(
            'Cybersource', 'batchPrefix'), time.strftime("%H%M"))

        s = config.get('Cybersource', 'header', vars={
            "merchantid": config.get('Cybersource', 'merchantId'),
            "batchid": batchId,
            "date": d,
            "email": config.get('Cybersource', 'statusEmail'),
            "recordCount": recordCount
        })

        return s + "\n"
    except Exception as e:
        raise e


def decodeOrderGroove(input_file):
    """ Decode OrderGroove function

    This is the main decode function
    It starts off reading in the csv file provided by Order Groove
    Then it it puts those into a dictionary
    then it decodes each of the Credit Card Numbers
    """
    cipher = AES.new(config.get(
        'OrderGroove', 'hashkey', raw=True).encode("ascii"), AES.MODE_ECB)
    ogcsv = open_csv(input_file)
    decodedDictionary = {}
    for row in ogcsv:
        try:
            if len(row) > 0:
                enc_cc_exp_date = row["CC Expiration Date"].strip()
                card_expirationMonth, card_expirationYear = decodeCardExpDate(decryptOrderGroove(
                    cipher, enc_cc_exp_date))
                rowdict = {
                    "paySubscriptionCreateService_disableAutoAuth": "TRUE",
                    "merchantReferenceCode": "ogsub" + row["OG Customer ID"].strip() + row["OG Public Payment ID"].strip()[:5],
                    "merchantDefinedData_field1": row["OG Customer ID"].strip(),
                    "merchantDefinedData_field2": enc_cc_exp_date,
                    "merchantDefinedData_field3": int(decodeCardType(row["CC Type"].strip())),
                    "merchantDefinedData_field4": row["OG Public Payment ID"].strip(),
                    "billTo_firstName": row["Billing First"].strip(),
                    "billTo_lastName": row["Billing Last"].strip(),
                    "billTo_street1": row["Billing Address 1"].strip(),
                    "billTo_street2": row["Billing Address 2"].strip(),
                    "billTo_city": row["Billing City"].strip(),
                    "billTo_state": row["Billing State"].strip(),
                    "billTo_postalCode": row["Billing Zip"].strip()[:5],
                    "billTo_country": row["Billing Country"].strip(),
                    "billTo_phoneNumber": row["Billing Phone"].strip(),
                    "billTo_email": row["Email Address"].strip(),
                    "card_accountNumber": decryptOrderGroove(
                        cipher, row["CC Number"].strip()),
                    "card_expirationMonth": card_expirationMonth,
                    "card_expirationYear": card_expirationYear,
                    "card_cardType": decodeCardType(row["CC Type"].strip())
                }
                trace(5, "%s" % rowdict)
                decodedDictionary[row["OG Public Payment ID"].strip()
                                  ] = rowdict
            else:
                trace(3, "Row length was 0")
        except Exception as error:
            print("Error! %s had the following error %s" %
                  (row["OG Public Payment ID"], error))
    return decodedDictionary


# ## Output Writer
def writeOutput(dictionary, ofile):
    """ Function that will write the output file for Cybersource """
    f = open(ofile, "w")
    f.write(formatCyberSourceCSVHeader(len(dictionary)))
    f.write("\n")
    csvfile = csv.DictWriter(f, dialect='excel',
                             fieldnames=config.get('Cybersource', 'columnNames').split(','))
    csvfile.writeheader()
    for key, rowdict in dictionary.items():
        try:
            csvfile.writerow(rowdict)
        except Exception as error:
            print("Error! %s had the following error %s" % (error, rowdict))
    f.write("\n")
    f.write("END,SUM=0")
    f.write("\n")
    f.write("\n")
    f.close()


# # This is the main Function for decodeOrderGroove.py
# #  This is where it all starts. The Main Function
if __name__ == '__main__':
    # # Set up global variables
    # Note: We must use Raw Config Parser to prevent interpolation of '%' and other weird characters
    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))
    inputfile = config.get('Base', 'input_file')
    outputfile = config.get('Base', 'tocyb_file')
    trace(3, "Output file is  %s" % outputfile)

    # Open & Decode File
    decodedDictionary = decodeOrderGroove(inputfile)

    # Write output file
    writeOutput(decodedDictionary, outputfile)
