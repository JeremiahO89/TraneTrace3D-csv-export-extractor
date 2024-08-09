import os, csv

# open a csv with the keywords to search for
def getKeyWords():
    assert "Keywords.csv" in os.listdir(os.path.dirname(__file__)), errorReport("Keyword File")   # check to make sure keywords file is there

    #Keywords.csv file should have first row as the keywords to search for, separated by commas, second row should have the words the data maps to
    target_path = os.path.join(os.path.dirname(__file__), "Keywords.csv")
    with open(target_path, "r") as the_file:
        contents = the_file.readlines()

    inputkeywords = contents[0].strip("\n").split(",")
    outputKeywords = contents[1].strip("\n").split(",")
    return (inputkeywords,outputKeywords)

# read all of the trace data
def readData():
    # get the .csv file from the current folder
    filename = "none"
    for names in os.listdir(os.path.dirname(__file__)):
        if (".csv" in names) and (names != "Keywords.csv"):
            filename = names
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
        
    # out_path = os.path.join(os.path.dirname(__file__), 'List.txt')
    # with open(out_path, 'w') as out_file:
    #     for line in fileContents:
    #         data = cleanLine(line)
    #         out_file.write(f"{data}\n")

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

        else: # get the other data
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
def dataDictionary_toCSV(spliceContents):

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

    out_path = os.path.join(os.path.dirname(__file__), fileName)    # file to write output data
    with open(out_path, 'w') as out_file:
        out_file.write(header + "\n")

        for key in dic: # for every room in the dictionary write its data to the output file
            file_string = ""
            file_string += (str(key) + ",")

            for pos in range(1, len(headerList)):
                keyword = headerList[pos]
                file_string += (str(dic[key][keyword]) + ",")

            out_file.write(f"{file_string}\n")

# # execute the code
keywords = getKeyWords()
data = spliceData(keywords,readData())
dataDictionary_toCSV(data)
print("Done")
