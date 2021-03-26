#!/usr/bin/python
"""
Created on Mar 25, 2021

combineOrderGrooveATG.py

Script was created to combine credit card info from OrderGroove
and with the Oracle ATG extract

@author: dougrob
"""

import configparser
import csv
# import os
# import re
import sys
import base64
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


def combineOrderGroove(input_file, atgPayments):
    """ Import OrderGroove function

    This is the main import function
    It starts off reading in the csv file provided by Order Groove
    Then it it puts those into a dictionary
    """
    ogcsv = open_csv(input_file)
    goodRows = {}
    badRows = {}
    for row in ogcsv:
        if len(row) > 0:
            ycccustid = row["YC Customer ID"].strip()
            label = row["Payment Label"].strip()
            if label != "PayPal":
                label = "CreditCard"

            try:
                token = atgPayments[ycccustid + label]
            except Exception as error:
                token = ""

            ogpayid = row["OG Payment Public ID"].strip()

            rowdict = {
                "OGPaymentID": row["OG Payment ID"].strip(),
                "OGCustomerID": row["OG Customer ID"].strip(),
                "PaymentLabel": label,
                "TokenID": token,
                "OGPaymentPublicID": ogpayid,
                "YCCustomerID": ycccustid
            }

            if token != "":
                trace(2, "good - %s" % rowdict)
                goodRows[ogpayid] = rowdict
            else:
                trace(2, "bad - %s" % rowdict)
                badRows[ogpayid] = rowdict
        else:
            trace(3, "Row length was 0")
    return goodRows, badRows


def importATG(creditcard_file, paypal_file):
    """ import ATG function

    This is function creates a payment map that we can use to fill in the token ids 
    for OrderGroove
    """
    cccsv = open_csv(creditcard_file)
    decodedDictionary = {}
    for row in cccsv:
        try:
            if len(row) > 0:
                custId = row["OG Customer ID"].strip()
                label = "CreditCard"
                token_id = row["SUBSCRIPTION_ID"].strip()
                trace(5, "%s,%s,%s" % (custId, label, token_id))
                decodedDictionary[custId + label] = token_id
            else:
                trace(3, "Row length was 0")
        except Exception as error:
            print("Error! %s had the following error %s" %
                  (row["OG Customer ID"].strip(), error))
    pplcsv = open_csv(paypal_file)
    for row in pplcsv:
        try:
            if len(row) > 0:
                custId = row["OG Customer ID"].strip()
                label = "PayPal"
                token_id = row["BILL_AGRMNT_ID"].strip()
                trace(5, "%s,%s,%s" % (custId, label, token_id))
                decodedDictionary[custId + label] = token_id
            else:
                trace(3, "Row length was 0")
        except Exception as error:
            print("Error! %s had the following error %s" %
                  (row["OG Customer ID"].strip(), error))
    return decodedDictionary


# ## Output Writer
def writeOutput(rows, ofile):
    """ Function that will write the output file for Cybersource """
    csv = open_csv(ofile, "w", config.get(
        'OrderGroove', 'outputColumnNames').split(','))
    csv.writeheader()
    for k in rows.keys():
        csv.writerow(rows[k])


# # This is the main Function for decodeOrderGroove.py
# #  This is where it all starts. The Main Function
if __name__ == '__main__':
    # # Set up global variables
    # Note: We must use Raw Config Parser to prevent interpolation of '%' and other weird characters
    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))
    inputfile = config.get('Base', 'input_file')
    creditcard_file = config.get('Base', 'atg_cc_file')
    paypal_file = config.get('Base', 'atg_ppl_file')
    outputfile = config.get('Base', 'output_file')
    trace(3, "Output file is  %s" % outputfile)

    # Open & Decode File
    atgPayments = importATG(creditcard_file, paypal_file)

    goodrows, badrows = combineOrderGroove(inputfile, atgPayments)

    # Write output file
    writeOutput(goodrows, outputfile)

    # Write bad file
    writeOutput(badrows, outputfile + ".bad")
