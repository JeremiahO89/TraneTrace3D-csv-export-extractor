Download Python 3.0 or newer from Google.

Put your ".csv" file in the same folder as the TrainConver.py and Keywords.csv file. The ".csv" file can either be a zone or room report from Trane Trace 3D
Right Click on the TrainConverter.py file and open with Python 3.0 (or whatever version of Python you downloaded).

A file named "Room Load Summary.csv" or "Zone Load Summery.csv" should appear in the folder with your original .csv file and python files, this new csv file is the cleaned data file.

You can now open this file with excel.
You're all done!



Warning!:
When you run the python script only one new .csv file can be in the folder 
The name of your new file does not matter but it needs to be a .csv type
If there is more than one new .csv file the program does not know which one to open and it can/will fail.
If a file named Error Report is outputed somthing failed check the report and you might be able to fix the issue.


Changing Values:
If you are noticing that the values in the cleaned file don't match what they should, open the keywords.csv file and look to see if the keyword in the first row matches the keyword in the trace csv file you want.
When trace does updates they can change the words in their export file. For example "Number of People" changed to “No People (max)” in one of the updates. If you notice that the keyword is different from the value you want, change that word and save the file. If there are other keywords you would like you can add them.
The second row is the header you would like for that keyword to map to in the new file, This most likely will not need to change but it's there for customization. These can’t be blank if you are adding new keywords to the file.  


If any other problems arise, send an email to jjo5541@psu.edu with the trace file you are trying to clean, and a zip of the Trace TrainConver program you are using.
Created By: Jeremiah J Ondrasik