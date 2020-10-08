#!/usr/bin/python
"""
Created on Oct 08, 2020

decodeOrderGroove.py

Script was created to decrypt credit card info
and then create file to be sent to OrderGroove for processing

@author: dougrob
"""

import configparser
import os
import re
import sys
import time # For PYthon 2.4
import smtplib


def open_file(fname, t="r"):
    """Function to open a file"""
    fhand = open(fname, t)
    return fhand

def trace(level, string):
    """Trace function"""
    if level <= int(config.get('Debug', 'LogLevel')):
        print('%s' % string)
        sys.stdout.flush()


# # This is the main Function for decodeOrderGroove.py
# #  This is where it all starts. The Main Function
if __name__ == '__main__':
    # # Set up global variables
    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))
    outputfile = config.get('Base', 'output_file')
    trace(3, "Output file is  %s" % outputfile)