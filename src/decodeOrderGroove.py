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
import os
import re
import sys
import time  # For PYthon 2.4
import smtplib


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
    if(string.equals)

# ## This is the main decode function
# ## It starts off reading in the csv file provided by Order Groove
# ## Then it it puts those into a dictionary
# ## then it decodes each of the Credit Card Numbers


def decodeOrderGroove(input_file):
    """ Decode OrderGroove function """
    ogcsv = open_csv(input_file)
    decodedDictionary = ""
    for row in ogcsv:
        try:
            if len(row) > 0:
                ogsubid = row[5].strip()
                enc_cc_exp_date = row[22].strip()
                billTo_firstName = row[23].strip()
                billTo_lastName = row[24].strip()
                billTo_street1 = row[25].strip()
                billTo_street2 = row[26].strip()
                billTo_city = row[27].strip()
                billTo_state = row[28].strip()
                billTo_postalCode = row[29].strip()
                billTo_country = row[31].strip()
                billTo_phoneNumber = row[32].strip()
                billTo_email = row[6].strip()
                card_accountNumber = row[20].strip()
                card_expirationMonth = "10"
                card_expirationYear = "2022"
                card_cardType = decodeCardType(row[21].strip())

                trace(4, "Row is %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (ogsubid, enc_cc_exp_date, billTo_firstName, billTo_lastName, billTo_street1, billTo_city,
                                                                                                billTo_state, billTo_postalCode, billTo_country, billTo_phoneNumber, billTo_email, card_accountNumber, card_expirationMonth,
                                                                                                card_expirationYear, card_cardType)
                      )
                decodedDictionary += "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (ogsubid, enc_cc_exp_date, billTo_firstName, billTo_lastName, billTo_street1, billTo_street2, billTo_city,
                                                                                                           billTo_state, billTo_postalCode, billTo_country, billTo_phoneNumber, billTo_email, card_accountNumber, card_expirationMonth,
                                                                                                           card_expirationYear, card_cardType)
            else:
                trace(3, "Row length was 0")
        except ValueError as error:
            print(error)
    return decodedDictionary


# ## Output Writer
def writeOutput(dictionary, ofile):
    """ Function that will write the output file for Cybersource """
    f = open(ofile, "w")
    # Need to get the header string
    # Note must have number of records
    # s = getHeader(len(dictionary))
    s = dictionary
    f.write('%s' % s)
    # s = getCsvColums()
    # f.write('%s' % s)
    # s = getRecords()
    # f.write('%s' % s)
    f.close()
    trace(2, 'File was writen with %s' % s)


# # This is the main Function for decodeOrderGroove.py
# #  This is where it all starts. The Main Function
if __name__ == '__main__':
    # # Set up global variables
    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))
    inputfile = config.get('Base', 'input_file')
    outputfile = config.get('Base', 'output_file')
    trace(3, "Output file is  %s" % outputfile)

    # Open & Decode File
    decodedDictionary = decodeOrderGroove(inputfile)

    # Write output file
    writeOutput(decodedDictionary, outputfile)
