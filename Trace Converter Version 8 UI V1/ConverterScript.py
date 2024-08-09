import os
import csv
import sys

# open a csv with the keywords to search for
def resource_path(fileName):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in `_MEIPASS`
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, fileName)
def getKeyWords():
    # Check if the CSV file exists in the bundled environment
    csv_file_name = "Keywords.csv"
    target_path = resource_path(csv_file_name)

    if not os.path.isfile(target_path):
        raise FileNotFoundError(f"{csv_file_name} not found at {target_path}")

    # Read the contents of the CSV file
    with open(target_path, "r") as the_file:
        contents = the_file.readlines()

    inputkeywords = contents[0].strip("\n").split(",")
    outputKeywords = contents[1].strip("\n").split(",")
    return (inputkeywords,outputKeywords)

# read all of the trace data
def readData(filename):
    # get the .csv file from the current folder
    # check to see if it found the folder
    assert ".csv" in filename, errorReport("Data File")
    # open and read the file
    target_path = os.path.join(os.path.dirname(__file__), filename)
    with open(target_path, "r") as the_file:
        content = the_file.readlines()
    return content

# used for error reports
def errorReport(fileType):
    out_path = os.path.join(os.path.dirname(__file__), 'Python Error Report.txt')
    with open(out_path, 'w') as out_file:
        out_file.write(f"No Valid {fileType} in the Folder: \n")
        out_file.write(str(os.path.dirname(__file__)) + "\n")
        out_file.write("List of the Files in this folder  \n\n")
        out_file.write(str(os.listdir(os.path.dirname(__file__))))
    raise ValueError ("No cvs file to read")

# remove the junk from the lines of data
def cleanLine(line):
        line = line.strip("\n")
        #look for and combine any numbers > 999
        start = 0
        while start < len(line)-1:
            start_char = line[start]
            if start_char == '"' or start_char == "'":
                end = start+1
                while (line[end] != '"'):
                    end += 1
                end_char = line[end]
                if end_char == '"' or end_char == "'":
                    #grab and edit the number remove quotations and comma
                    num = line[start:end + 1]
                    num = num.strip("'").strip('"').split(",")
                    num = ''.join(num)
                    try: # checks if the string was a number
                        float(num)
                        # recreate the string
                        front_half = line[:start]
                        back_half = line[end+1:]
                        line = front_half+num+back_half
                        start = start + len(num) # skip to the next char after the number
                    except: # else don't change anything
                        start = end + 1 #skip to the next char (the one after the ending quote)
            else:
                start += 1
                    
        line = line.split(",")
        data = list(filter(None, line)) # remove empty strings
        return data

# splice the data file up into a dictionary
def spliceData(keywords, fileContents):
    """
    Pre: keywords -> tuple of a 2 lists of strings (pos 0: inputkeywords, pos1: outputkeywords)
    Post: return a dict
    dict -> keys are strings from keywords, values are data from fileContents
    """

    inputkeywords = keywords[0]
    outputkeywords = keywords[1]

    allDataByArea = {}  # dict to store the data
    currentArea= None   # string with current spot in allDataByArea
    room_or_zone = True # true if a room file, false if a zone file

    for line in fileContents:
        data = cleanLine(line)
        if (inputkeywords[0] in data[0]):  # check for Room file type
            currentArea = data[0].removeprefix(inputkeywords[0])
            setUpNewArea(allDataByArea, currentArea, outputkeywords)
        elif (inputkeywords[1] in data[0]): # check for Zone file type
            currentArea = data[0].removeprefix(inputkeywords[1])
            setUpNewArea(allDataByArea, currentArea, outputkeywords)
            room_or_zone = False

        # I was unable to abstract the sensible and latent data table
        # This is a hard code fix to the issue
        elif ("Grand Total" in data):
            cooling_or_heating = True # var for if the current section is cooling or heating
            for data_pos in range(len(data)):
                if ("Grand Total" in data[data_pos]) and cooling_or_heating:
                    # first pass would be the cooling section
                    allDataByArea[currentArea]['Instant Sensible Cooling'] = data[data_pos + 1]
                    allDataByArea[currentArea]['Delay Sensible Cooling'] = data[data_pos + 2]
                    allDataByArea[currentArea]['Latent Cooling'] = data[data_pos + 3]
                    allDataByArea[currentArea]['Total Cooling Load'] = data[data_pos + 4]
                    cooling_or_heating = False
                elif ("Grand Total" in data[data_pos]) and not cooling_or_heating:
                    allDataByArea[currentArea]['Instant Sensible Heating'] = data[data_pos + 1]
                    allDataByArea[currentArea]['Delay Sensible Heating'] = data[data_pos + 2]
                    allDataByArea[currentArea]['Latent Heating'] = data[data_pos + 3]
                    allDataByArea[currentArea]['Total Heating Load'] = data[data_pos + 4]

        else: # get the other data labled in the keywords.csv file
            for key_pos in range(2,len(inputkeywords)):    
                for data_pos in range(len(data)):
                    if inputkeywords[key_pos] in data[data_pos]:
                        allDataByArea[currentArea][outputkeywords[key_pos]] = data[data_pos+1]       

    return (allDataByArea, room_or_zone)

# set up a new area in the dictionary
def setUpNewArea(dic,room, keys):

    """
    pre:
        dic -> dic to add data too
        room -> string used for key
        keys -> a list of strings which will be used a keys in the nested dictionary and initiated as zero
    post: 
        Nothing
    """
    dic[room] = {}
    for pos in range(2,len(keys)): # skip the first 2 since they are not used in the nested dict (ROOM_,ZONE_)
        dic[room][keys[pos]] = 0

# write the dictionary to a CSV
def dataDictionary_toCSV(spliceContents, save_file_path):
    # inputkeywords = keywords[0]
    # outputkeywords = keywords[1]
    dic = spliceContents [0]
    room_or_zone = spliceContents[1]

    if room_or_zone: 
        fileName = 'Room Load Summary.csv'
        headerList = ["Room Name"]
    else: 
        fileName = 'Zone Load Summary.csv'
        headerList = ["Zone Name"]

    # make the header
    firstRoom = list(dic.keys())[0]
    headerList += list(dic[firstRoom].keys())
    header = ','.join(headerList)

    # make a unique output file (checks if the file already exits)
    out_path = os.path.join(save_file_path, fileName)    # file to write output data
    counter = 1
    while os.path.exists(out_path):
        directory, file_name = os.path.split(out_path)
        file_name = file_name.split('.')
        if not any(char.isdigit() for char in file_name[0]):
            file_name[0] = file_name[0] + f"({str(counter)})"
        else:
            file_name[0] = file_name[0][:-3] + f"({str(counter)})"
        file_name = ".".join(file_name)
        out_path =  os.path.join(directory, file_name)
        counter+=1
        

    with open(out_path, 'w') as out_file:
        out_file.write(header + "\n")
        for key in dic: # for every room in the dictionary write its data to the output file
            file_string = ""
            file_string += (str(key) + ",")

            for pos in range(1, len(headerList)):
                keyword = headerList[pos]
                file_string += (str(dic[key][keyword]) + ",")

            out_file.write(f"{file_string}\n")
    return out_path






# Code for the desktop display

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import platform

version_number = 1.0

fetch_file_path_global = None

if platform.system() == "Windows":
    save_file_path_global = os.path.join(os.environ["USERPROFILE"], "Downloads")
else:
    save_file_path_global = None

def select_file_location():
    # set the default file folder
    if platform.system() == "Windows":
        default_directory = os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        default_directory = None

    # pick a file
    file_path = filedialog.askopenfilename(
        initialdir = default_directory,
        title = "Select a .CSV File:",
        filetypes = (("CSV files", "*.csv"), ("all files" , "*.*"))
    )
    
    if file_path:
        # update the global variable
        global fetch_file_path_global
        fetch_file_path_global = file_path
        # update the screen texts
        fileLabel.config(text= f"Selected File: {fetch_file_path_global}")
        statusLabel.config(text= "Converter is ready to run.")
    else:
        fileLabel.config(text= "No File Selected")

def select_directory_for_download():
        # set the default file folder
    if platform.system() == "Windows":
        default_directory = os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        default_directory = None

    # pick a file
    path = filedialog.askdirectory(
        initialdir = default_directory,
        title = "Select a Folder"
    )
    
    if path:
        # update the global variable
        global save_file_path_global
        save_file_path_global = path
        # update the screen texts
        saveLocationLabel.config(text= f"Selected File: {save_file_path_global}")
        statusLabel.config(text= "Converter is ready to run.")
    else:
        fileLabel.config(text= "No File Selected")



def run_on_click_button():
    # execute the code
    keywords = getKeyWords()
    data = spliceData(keywords,readData(fetch_file_path_global))
    savedFileName = dataDictionary_toCSV(data, save_file_path_global)
    statusLabel.config(text = f"Converter Ran Sucessfully. File Saved as: {savedFileName}")


#base window stuff
root = tk.Tk()
root.title("Trane Trace Converter" + " " + str(version_number))
root.geometry("1000x400")


# container for tabs
programWin = ttk.Notebook(root)
programWin.pack(fill="both", expand=True)

#first tab Main Progam
mainPage = tk.Frame(programWin)
mainPage.grid_columnconfigure(0, weight=1) # center on page
programWin.add(mainPage, text="Main Program") # add to tab container

#make frames for text
select_frame = tk.Frame(mainPage)
select_frame.grid(row=0, column=0, padx=5, pady=5)
save_frame = tk.Frame(mainPage)
save_frame.grid(row=1, column=0, padx=5, pady=5)
run_frame = tk.Frame(mainPage)
run_frame.grid(row=2, column=0, padx=5, pady=5)

#add text and buttons
fileLabel = tk.Label(select_frame, text = f"Selected File: {fetch_file_path_global}")
fileLabel.grid(row=0, column=0, padx=10, pady=10)
select_file_button = tk.Button(select_frame, text="Select File", command = select_file_location)
select_file_button.grid(row=1, column=0, padx=10, pady=5)

saveLocationLabel = tk.Label(save_frame, text = f"Selected Save Location: {save_file_path_global}")
saveLocationLabel.grid(row=0, column=0, padx=10, pady=10)
select_file_button = tk.Button(save_frame, text="Change Save Location", command = select_directory_for_download)
select_file_button.grid(row=1, column=0, padx=10, pady=5)

statusLabel = tk.Label(run_frame, text = "No file selected to run converter on.")
statusLabel.grid(row=2, column=0, padx=5, pady=10)
run_on_click_button = tk.Button(run_frame, text="Run Converter", command = run_on_click_button)
run_on_click_button.grid(row=2, column=1, padx=5, pady=10)

# seccond tab Keywords Page
keywordsPage = tk.Frame(programWin)
keywordsPage.grid_columnconfigure(0, weight=1) # center on page
programWin.add(keywordsPage, text="Keywords Page")

# run the program
root.mainloop()