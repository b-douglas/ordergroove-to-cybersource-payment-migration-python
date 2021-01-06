#!/usr/bin/python
"""
Created on Oct 20, 2020

encodeOrderGroove.py

Script was created to encode the CyberSource output file to be processed by OrderGrove file format.

@author: dougrob
"""

import configparser
import csv
import sys


# ## Function to open a file as a csv
# ##  All of the files are treated as a Csv, whether they are true CSVs or not.
# ## The reason for this is so that if a file needs more columns we have that ability
def open_csv(fname, t="r", fieldnames=""):
    """ Function to open a csv file """
    fhand = open(fname, t)
    if t == "r":
        csvfile = csv.DictReader(
            fhand, dialect='excel', quoting=csv.QUOTE_ALL)
    else:
        csvfile = csv.DictWriter(
            fhand, dialect='excel', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
    return csvfile


def trace(level, string):
    """ Trace function """
    if level <= int(config.get('Debug', 'LogLevel')):
        print('%s' % string)
        sys.stdout.flush()


def decodeCybersource(input_file):
    """ Decode Cybersource function

    This is the main decode function
    It starts off reading in the csv file provided by Cybersource
    Then it it puts those into a dictionary
    """
    ogcsv = open_csv(input_file)
    goodRows = {}
    badRows = {}
    for row in ogcsv:
        try:
            if len(row) > 0:
                status = row["reason_code"].strip()

                rowdict = {
                    "OGPublicPaymentID": row["merchant_defined_data4"].strip(),
                    "cybersourceToken": row["request_id"].strip(),
                    "ccExpDate": row["merchant_defined_data2"].strip(),
                    "ccType": row["merchant_defined_data3"].strip(),
                    "cybstatus_optional": row["reason_code"].strip()
                }

                if(status == "100"):
                    trace(2, "good - %s" % rowdict)
                    goodRows[row["merchant_defined_data4"].strip()] = rowdict
                else:
                    trace(2, "bad - %s" % rowdict)
                    badRows[row["merchant_defined_data4"].strip()] = rowdict
            else:
                trace(1, "Row length was 0")
        except Exception as error:
            print("%s had the following error %s" %
                  (row["request_id"].strip(), error))
    return goodRows, badRows


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
    inputfile = config.get('Base', 'fromcyb_file')
    outputfile = config.get('Base', 'toog_file')
    trace(3, "Output file is  %s" % outputfile)

    # Open & Decode File
    goodrows, badrows = decodeCybersource(inputfile)

    # print(goodrows)
    # print("######")
    # print(badrows)
    # Write good file
    writeOutput(goodrows, outputfile)

    # Write bad file
    writeOutput(badrows, outputfile + ".bad")
