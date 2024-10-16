import os
import csv
import sys

# open a csv with the keywords to search for
def resource_path(fileName):
    """ Get absolute path to the file, looking in the directory of the executable """
    if getattr(sys, 'frozen', False):
        # If the application is compiled with PyInstaller, get the directory of the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Otherwise, use the directory of the script
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, fileName)

def getKeyWords():
    # Check if the CSV file exists in the directory with the executable
    csv_file_name = "Keywords.csv"
    target_path = resource_path(csv_file_name)

    if not os.path.isfile(target_path):
        raise FileNotFoundError(f"{csv_file_name} not found at {target_path}")

    # Read the contents of the CSV file
    with open(target_path, "r") as the_file:
        contents = the_file.readlines()

    inputkeywords = contents[0].strip("\n").split(",")
    outputKeywords = contents[1].strip("\n").split(",")
    return (inputkeywords, outputKeywords)

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
            try:
                if start_char == '"':
                        end = start+1
                        while (line[end] != '"'):
                            end += 1
                        end_char = line[end]
                        if end_char == '"':
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
            except:
                    print("ERROR_THIS_LINE:" + line)
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
from tkinter import font as tkFont
from tkinter import ttk
import platform

version_number = 1.1

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
    
    global fetch_file_path_global
    fetch_file_path_global = file_path
    
    if fetch_file_path_global:
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
root.geometry("1200x800")

# container for tabs
programWin = ttk.Notebook(root)
programWin.pack(fill="both", expand=True)

#first tab operion details
howToPage = tk.Frame(programWin)
programWin.add(howToPage, text="Operation Details")  # Add to tab container

aboutMeText = """
Operation Details:
    - Select the .csv Trane Trace file you are trying to clean.
    - The Trane Trace file can be either a Room Summary, or a Zone Summary file.
    - Select a location to save the cleaned file too, the default is your Downloads folder.
    - Click "Run Converter". 
    - A file named "Room Load Summary.csv" or "Zone Load Summery.csv" should appear in the selected save location.
    
    You are now done and can open this file with excel.

Additional Notes:
    If you are noticing that the values in the cleaned file don't match what they should:
    Click on the "Keywords Page" (at the top) and check that the "Words to search for:" row has keywords that match the values you are searching for in the Trace.csv file.
    When trace does updates they can change the words in their export files. For example "Number of People" changed to “No People (max)” in one of the updates. If you notice that the keyword is different from the value you want, change that word and save the file.
    If there are other keywords you would like to clean, you can add them or remove them.
    The second row ("Map words to label:") is the header you would like for that keyword to map to in the new file. These CAN NOT be blank or identical.
    You must SAVE before running after making any changes.

Other notes:
    The "Keywords.csv" file must be in the same folder as the Trance Trace Program.exe file. This is where the keywords are stored for future use. You can also edit the keywords here with excel instead of using the Keywords page.

If any other problems arise, send an email to jjo5541@psu.edu with the trace file you are trying to clean, a zip of the Trace Trace Export Converter program with the "Keywords.csv" file you are using.
Created By: Jeremiah J Ondrasik (8/12/2024)
"""

textScrollbar = tk.Scrollbar(howToPage, orient="vertical")
textScrollbar.pack(side="right", fill="y")

textWidget = tk.Text(howToPage, wrap=tk.WORD, yscrollcommand=textScrollbar.set, font=tkFont.Font(family="Arial", size=10))  # Wrap words and bind scrollbar
textWidget.insert(tk.END, aboutMeText)
textWidget.pack(fill="both", expand=True)  # Fill container and allow expansion
textWidget.config(state=tk.DISABLED)  # Disable editing
textScrollbar.config(command=textWidget.yview)  # Link scrollbar to text widget



#seccond tab Main Progam
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



# third tab Keywords Page
keywordsPage = tk.Frame(programWin)
keywordsPage.grid_columnconfigure(0, weight=1) # center on page
programWin.add(keywordsPage, text="Keywords Page")

# scrolling code
def on_frame_configure(canvas):
    canvas.configure(scrollregion = canvas.bbox("all"))


excelChartContainer = tk.Frame(keywordsPage)
excelChartContainer.grid_columnconfigure(0, weight=1) # center on page
excelChartContainer.grid(row=0, column=0, padx=5, pady=5)

excellScrollCanvas = tk.Canvas(excelChartContainer,height=90, width=1000)
excell_h_scrollbar = tk.Scrollbar(excelChartContainer, orient = "horizontal", command = excellScrollCanvas.xview)
excellScrollCanvas.configure(xscrollcommand=excell_h_scrollbar.set)

excellScrollCanvas.pack(side = "top", fill="both", expand=True)
excell_h_scrollbar.pack(side = "bottom", fill = "x")


excelChart = tk.Frame(excellScrollCanvas)
excellScrollCanvas.create_window((0,0),window=excelChart, anchor="nw")
excelChart.bind("<Configure>", lambda event, canvas=excellScrollCanvas: on_frame_configure(excellScrollCanvas))

keywordButtons = tk.Frame(keywordsPage)
keywordButtons.grid_columnconfigure(0, weight=1) # center on page
keywordButtons.grid(row=2, column=0, padx=5, pady=5)



keywordData = [] # is a blank list at the start

def loadSavedKeywords():
    global keywordData
    keywords = getKeyWords()
    keywordData = [keywords[0], keywords[1]]
    updateKeywords()
    statuskeywordLabel.config(text = f"File Loaded")
    

def updateKeywords():
    # Clear any existing widgets in the frame
    for widget in excelChart.winfo_children():
        widget.destroy()

    global keywordData
    for r, row in enumerate(keywordData):
        if r == 0:
            searchKeywordsLabel = tk.Label(excelChart, text = f"Words to search for:")
            searchKeywordsLabel.grid(row=0, column=0,  padx=3, pady=5)
        elif r == 1:
            mapKeywordsLabel = tk.Label(excelChart, text = f"Map words to label:")
            mapKeywordsLabel.grid(row=1, column=0,  padx=3, pady=5)


        for c, val in enumerate(row):
            entry = tk.Entry(excelChart, width=max(len(val), 15))  # Set initial width based on text length
            entry.grid(row=r, column=c+1, padx=3, pady=3, sticky="nsew")  # Add buffer and center the text box
            entry.insert(tk.END, val)

            # Bind the event to dynamically adjust width
            entry.bind("<KeyRelease>", lambda event, e=entry: adjust_width(e))


def adjust_width(entry):
    # Adjust the width of the Entry widget and update the value in the keyword lis
    content = entry.get()
    positionColumn = entry.grid_info()['column']
    positionRow = entry.grid_info()['row']
    global keywordData
    keywordData[positionRow][positionColumn-1] = content
    new_width = max(len(content), 15)  # Ensure a minimum width
    entry.config(width=new_width)


def add_column():
    global keywordData
    for row in keywordData:
        row.append("None")
    updateKeywords()
    
def remove_column():
    global keywordData
    for row in keywordData:
        if len(row) != 0:
            row.pop()        
    updateKeywords()
    
def saveKeywords():
    global keywordData
    csv_file_name = "Keywords.csv"
    target_path = resource_path(csv_file_name)

    if not os.path.isfile(target_path):
        raise FileNotFoundError(f"{csv_file_name} not found at {target_path}")

    # Read the contents of the CSV file
    with open(target_path, "w") as out_file:
        out_file.write(",".join(keywordData[0]) + "\n")
        out_file.write(",".join(keywordData[1]) + "\n")
    
    statuskeywordLabel.config(text = f"Keywords saved to file.")
    
buttonRowLocation = 5

loadKeywordsButton = tk.Button(keywordButtons, text="Load Saved Keywords", command = loadSavedKeywords)
loadKeywordsButton.grid(row=buttonRowLocation, column=0, padx=5, pady=5)

# Add the button to add another column
add_column_button = tk.Button(keywordButtons, text="Add Column", command = add_column)
add_column_button.grid(row=buttonRowLocation, column=1, padx=5, pady=5)

remove_column_button = tk.Button(keywordButtons, text="Remove Column", command = remove_column)
remove_column_button.grid(row=buttonRowLocation, column=2, padx=5, pady=5)

save_button = tk.Button(keywordButtons, text="Save Keywords", command = saveKeywords)
save_button.grid(row=buttonRowLocation, column=4, padx=5, pady=5)

statuskeywordLabel = tk.Label(keywordsPage, text = "")
statuskeywordLabel.grid(row=buttonRowLocation+2, column=0, padx=5, pady=10)

# run the program
root.mainloop()