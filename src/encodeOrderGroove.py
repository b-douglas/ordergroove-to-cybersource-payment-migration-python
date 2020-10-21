#!/usr/bin/python
"""
Created on Oct 20, 2020

encodeOrderGroove.py

An additional quick script used encode the CSV that OrderGroove expects

@author: dougrob
"""

import configparser
import csv
# import os
# import re
import sys


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


def formatOGRecord(dct):
    """ Function to format a dictionary as a CSV record for OrderGroove"""
    try:
        s = "%s,%s,%s,%s,%s\n" % (dct["ogsubid"], dct["cybtoken"],
                                  dct["enc_cc_exp_date"], dct["card_cardType"], dct["ogpayid"])
        return s
    except Exception as e:
        raise e


def formatOGColumnNames():
    """ Function to format the correct CSV Header that OrderGroove expects"""
    try:
        s = config.get('OrderGroove', 'outputColumnNames')
        return s + "\n"
    except Exception as e:
        raise e


def decodeCybersource(input_file):
    """ Decode Cybersource function

    This is the main decode function
    It starts off reading in the csv file provided by Cybersource
    Then it it puts those into a dictionary
    """
    ogcsv = open_csv(input_file)
    goodRows = []
    badRows = []
    firstRow = True
    for row in ogcsv:
        try:
            if(config.getboolean('OrderGroove', 'hasHeaderRow') and firstRow):
                trace(4, "Skipping header row")
                firstRow = False
            elif len(row) > 0:

                status = row[17].strip()

                rowdict = {
                    "ogsubid": row[27].strip(),
                    "cybtoken": row[3].strip(),
                    "enc_cc_exp_date": row[28].strip(),
                    "card_cardType": row[30].strip(),
                    "ogpayid": row[29].strip()
                }

                if(status == "100"):
                    trace(2, "good - %s %s" % (rowdict, status))
                    goodRows.append(rowdict)
                else:
                    rowdict["ogpayid"] = row[29].strip() + "," + status
                    trace(2, "bad - %s" % rowdict)
                    badRows.append(rowdict)
            else:
                trace(3, "Row length was 0")
        except Exception as error:
            print("%s had the following error %s" % (row[5].strip(), error))
    return goodRows, badRows


# ## Output Writer
def writeOutput(rows, ofile):
    """ Function that will write the output file for Cybersource """
    f = open(ofile, "w")
    f.write(formatOGColumnNames())
    for rowdict in rows:
        f.write(formatOGRecord(rowdict))
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
    inputfile = config.get('Base', 'fromcyb_file')
    outputfile = config.get('Base', 'toog_file')
    trace(3, "Output file is  %s" % outputfile)

    # Open & Decode File
    goodrows, badrows = decodeCybersource(inputfile)

    # Write good file
    writeOutput(goodrows, outputfile)

    # Write bad file
    writeOutput(badrows, outputfile + ".bad")
