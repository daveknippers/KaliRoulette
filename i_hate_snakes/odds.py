import sqlite3
import csv
import os
import sys

class oddsEngine():
    oddsData = {}
    def __init__(self):
        if (os.path.exists("intialOdds.csv")):
            with open('intialOdds.csv') as csvfile:
                rawData = csv.reader(csvfile, delimiter = ' ')
                for row in rawData:
                    self.oddsData[row[0]]=row[1]
        else:
            print("There needs to be a intialOdds.csv or this cant happen.  Please check the git repo to make sure its  there.")
            sys.exit()
    def getOdds(self, condition1, condition2=None):
        if condition2 != None:
            try:
                odds1 = self.oddsData[condition1]
                odds2 = self.oddsData[condition2]
                pass
            except Exception as e:
                return -1
                raise
            finalOdds = int(odds1) * int(odds2)
        else:
            try:
                finalOdds = self.oddsData[condition1]
                pass
            except Exception as e:
                return -1
                raise
        return finalOdds
    def changeOdds(self, condition, newOdds):
        self.oddsData[condition] = newOdds

    def levelChangeOdds(self, level, hearts, items, rope, bombs):
        #do stuff
        return
