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
def open_csv(fname, t="r"):
    """Function to open a file"""
	fhand = open(fname, t)
	csvfile = csv.reader(fhand)
	return csvfile


def trace(level, string):
    """Trace function"""
    if level <= int(config.get('Debug', 'LogLevel')):
        print('%s' % string)
        sys.stdout.flush()

# ## This is the main decode function
# ## It starts off reading in the csv file provided by Order Groove
# ## Then it it puts those into a dictionary
# ## then it decodes each of the Credit Card Numbers


def decodeOrderGroove(input_file):
	ogcsv = open_file(input_file)
 	for row in ogcsv:
		try:
            if len(row) > 0:
                term = row[0].strip()
        except ValueError , error:
            print(error)

def writeOutput(dictionary, ofile):
    """Function that will write the output file for Cybersource """
    f = open_file(ofile, 'w')
    # Need to get the header string
    # Note must have number of records
    s = getHeader(len(dictionary))
    f.write('%s' % s)
    s = getCsvColums()
    f.write('%s' % s)
    s = getRecords()
    f.write('%s' % s)
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
    writeOutput(decodedDictionary,outputfile)

