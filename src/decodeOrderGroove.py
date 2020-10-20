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
# import smtplib


# ## Function to open a file as a csv
# ##  All of the files are treated as a Csv, whether they are true CSVs or not.
# ## The reason for this is so that if a file needs more columns we have that ability
def open_csv(fname):
    """ Function to open a csv file """
    fhand = open(fname, "r")
    csvfile = csv.reader(fhand)
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


def formatCyberSourceRecord(dct):
    """ Function to format a dictionary as a CSV record for Cybersource"""
    try:
        s = "TRUE,ogsub%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (dct["ogsubid"], dct["ogsubid"], dct["ogpayid"],
                                                                                      dct["enc_cc_exp_date"],
                                                                                      int(
                                                                                          dct["card_cardType"]),
                                                                                      dct["billTo_firstName"], dct["billTo_lastName"],
                                                                                      dct["billTo_street1"],
                                                                                      dct["billTo_street2"], dct["billTo_city"],
                                                                                      dct["billTo_state"], dct["billTo_postalCode"],
                                                                                      dct["billTo_country"],
                                                                                      dct["billTo_phoneNumber"],
                                                                                      dct["billTo_email"], dct["card_accountNumber"],
                                                                                      dct["card_expirationMonth"],
                                                                                      dct["card_expirationYear"], dct["card_cardType"])
        return s
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

# ## This is the main decode function
# ## It starts off reading in the csv file provided by Order Groove
# ## Then it it puts those into a dictionary
# ## then it decodes each of the Credit Card Numbers


def decodeOrderGroove(input_file):
    """ Decode OrderGroove function """
    cipher = AES.new(config.get(
        'OrderGroove', 'hashkey', raw=True).encode("ascii"), AES.MODE_ECB)
    ogcsv = open_csv(input_file)
    decodedDictionary = {}
    firstRow = True
    for row in ogcsv:
        try:
            if(config.getboolean('OrderGroove', 'hasHeaderRow') and firstRow):
                trace(4, "Skipping header row")
                firstRow = False
            elif len(row) > 0:
                enc_cc_exp_date = row[22].strip()
                card_expirationMonth, card_expirationYear = decodeCardExpDate(decryptOrderGroove(
                    cipher, enc_cc_exp_date))
                rowdict = {
                    "ogsubid": row[5].strip(),
                    "enc_cc_exp_date": enc_cc_exp_date,
                    "ogpayid": row[17].strip(),
                    "billTo_firstName": row[23].strip(),
                    "billTo_lastName": row[24].strip(),
                    "billTo_street1": row[25].strip(),
                    "billTo_street2": row[26].strip(),
                    "billTo_city": row[27].strip(),
                    "billTo_state": row[28].strip(),
                    "billTo_postalCode": row[29].strip()[:5],
                    "billTo_country": row[31].strip(),
                    "billTo_phoneNumber": row[32].strip(),
                    "billTo_email": row[6].strip(),
                    "card_accountNumber": decryptOrderGroove(
                        cipher, row[20].strip()),
                    "card_expirationMonth": card_expirationMonth,
                    "card_expirationYear": card_expirationYear,
                    "card_cardType": decodeCardType(row[21].strip())
                }
                trace(5, "%s" % rowdict)
                decodedDictionary[rowdict["ogsubid"] +
                                  rowdict["ogpayid"]] = rowdict
            else:
                trace(3, "Row length was 0")
        except Exception as error:
            print("%s had the following error %s" % (row[5].strip(), error))
    return decodedDictionary


# ## Output Writer
def writeOutput(dictionary, ofile):
    """ Function that will write the output file for Cybersource """
    f = open(ofile, "w")
    f.write(formatCyberSourceCSVHeader(len(dictionary)))
    f.write("\n")
    f.write(config.get('Cybersource', 'columnNames'))
    f.write("\n")
    for key, rowdict in dictionary.items():
        f.write(formatCyberSourceRecord(rowdict))
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
    outputfile = config.get('Base', 'output_file')
    trace(3, "Output file is  %s" % outputfile)

    print(formatCyberSourceCSVHeader(4))

    # Open & Decode File
    decodedDictionary = decodeOrderGroove(inputfile)

    # Write output file
    writeOutput(decodedDictionary, outputfile)
