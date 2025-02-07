# /**
#  * Sentiment Analysis Task
#  *
#  * This python script takes the name of a directory as a command line argument
#       and analyzes each .txt file in the directory for sentiment.  A report is
#       produced in the same directory containing the overall sentiment of the
#       collection of text files, as well as an individual sentiment analysis
#       of each file.
#  * @author      Kara Beason <beasonke@appstate.edu>
#  * @copyright   (c) 2019 Appalachian State University, Boone, NC
#  * @license     GNU General Public License version 3
#  */
from textblob import TextBlob
import os
import glob
import sys
import codecs
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
import csv
import re

# Check that a command line argument is present.
if len(sys.argv) != 2:
    print("Usage: python sentiments_analysis.py <directory>")
    exit(0)

directory = str(sys.argv[1])

# Check that the command line argurment is indeed a valid directory.
if (not os.path.isdir(directory)) or (not os.path.exists(directory)):
    print("Directory %s is not valid.", directory)
    exit(0)


# Check the current y position and whether the next line will run off the page.  
# Return a valid new y value.
def get_next_valid_y(report, y):
    width, height = letter
    if y - 100 < 0:
        # if the next line would run off the page/into the margin, 
        #   create a new page and start at the top of the next.
        report.showPage()
        y = height - 100
        return y
    else:
        y = y - 15
        return y


# Determine whether the polarity score (integer passed in)
#   is negative (green), neutral (grey), or positive (green)
def get_polarity_color(polarity):
    if polarity < -0.05:
        return '#FF0000'
    elif polarity > 0.05:
        return '#008000'
    else:
        return '#808080'


# Create the body of the report named report_name.
#   Sentiments_list is the list of individual sentiment analyses
#   and overall is the overall sentiment of the list.
def print_report(studentSentimentDict, overallSentiment, assignmentName):
    # PDF lab canvas creation
    reportPDF = canvas.Canvas("output.pdf", pagesize=letter)
    # although width is unused in this script it's apparently necessary for report lab.
    width, height = letter
    # decrease y for the top of page margin.
    y = height - 100
    # Print the overall sentiment analysis on the first page.
    reportPDF.drawString(100,y, "Assignment: "+assignmentName)
    y = get_next_valid_y(reportPDF, y)    
    reportPDF.drawString(100, y, "Overall Sentiment: ")
    y = get_next_valid_y(reportPDF, y)
    reportPDF.drawString(125, y, "Polarity:")
    y = get_next_valid_y(reportPDF, y)
    color = get_polarity_color(overallSentiment.polarity)
    reportPDF.setFillColor(HexColor(color))
    reportPDF.drawString(125, y, str(overallSentiment.polarity))
    reportPDF.setFillColor(HexColor('#000000'))
    y = get_next_valid_y(reportPDF, y)
    reportPDF.drawString(125, y, "Subjectivity:")
    y = get_next_valid_y(reportPDF, y)
    reportPDF.drawString(125, y, str(overallSentiment.subjectivity))
    y = get_next_valid_y(reportPDF, y)
    reportPDF.drawString(125,y,"Green=Positive (>.05), Grey=Neutral, Red=Negative(<-.05)")
    y = get_next_valid_y(reportPDF, y)
    reportPDF.drawString(125,y,"Subjectivity: Scale 0=Objective, 1=Very Subjective ")

    # new page.
    reportPDF.showPage()
    # create array for output to csv
    csvSave=[]
    csvSave.append(["assignment","user","sentiment","subjectivity"])
    # Sentiment Analysis by text file/ student
    for user, sentiment in studentSentimentDict.iteritems():
        username=user.split("(")[0]
        y = height - 100
        reportPDF.drawString(100, y, "Student Name: ")
        reportPDF.drawString(225, y, user)
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125, y, "Polarity:")
        y = get_next_valid_y(reportPDF, y)
        color = get_polarity_color(sentiment.polarity)
        reportPDF.setFillColor(HexColor(color))
        reportPDF.drawString(125, y, str(sentiment.polarity))
        reportPDF.setFillColor(HexColor('#000000'))
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125, y, "Subjectivity:")
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125, y, str(sentiment.subjectivity))
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125,y,"Green=Positive (>.05), Grey=Neutral, Red=Negative(<-.05)")
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125,y,"Subjectivity: Scale 0=Objective, 1=Very Subjective ")
        y = get_next_valid_y(reportPDF, y)
        reportPDF.drawString(125, y, "Assessments:")
        for word in sentiment.assessments:
            y = get_next_valid_y(reportPDF, y)
            reportPDF.drawString(125, y, str(word))
        reportPDF.showPage()
        csvSave.append([assignmentName,username,sentiment.polarity,sentiment.subjectivity])
    reportPDF.save()
    with open('output.csv','w') as writeFile:
        writer=csv.writer(writeFile)
        writer.writerows(csvSave)



# Create the sentiments dictionary.
studentSentimentsDict = dict()
overallText = ""
# Change working directory to the dir that was passed in.
os.chdir(directory)
#look for csv in directory
assignmentName=""
# Iterate over each text file in the directory
for fileName in glob.iglob('*.txt'):
    # Username will be the first part of the filename for the report.
    userName = fileName.split('_')[0]
    userFullName = fileName.split('_')[1]
    upos=fileName.find(userFullName)
    upos+=len(userFullName)
    apos=len(fileName)-4
    assignmentName=fileName[upos+1:apos]
    assignmentName=assignmentName.replace("_"," ")
    fileText = ""
    with codecs.open(fileName, "r",encoding='utf-8', errors='ignore') as fileData:
        # Read in the text file.
        fileText += fileData.read()
        # Add contents of text file to overall text.
        overallText += fileText
        # Convert to textblob object
        textBlobOutput = TextBlob(fileText)
        # Add sentiment assessment to sentiments dict under name <userfullname (username)>
        dictIndex = userFullName + " " + "(" + userName + ")"+" - "+assignmentName
        # Add the sentiment assessment of the text blob to the student sentiment dictionary under the student's name.
        studentSentimentsDict[dictIndex] = textBlobOutput.sentiment_assessments
# Convert entire text into a textblob object
overallTextBlobOutput = TextBlob(overallText)
# Get the sentiment assessment of the whole thing.
overallSentiment = overallTextBlobOutput.sentiment_assessments
# Create and save the report.
print_report(studentSentimentsDict, overallSentiment,assignmentName)