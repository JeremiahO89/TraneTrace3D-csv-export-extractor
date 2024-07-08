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
    Pre: keywords -> list of strings
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

        else: # get the other data
            for key_pos in range(2,len(inputkeywords)):    
                for data_pos in range(len(data)):
                    if inputkeywords[key_pos] in data[data_pos]:
                        allDataByArea[currentArea][outputkeywords[key_pos]] = data[data_pos+1]
        

    return (allDataByArea, room_or_zone)

# set up a blank area in the dictionary
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
def dataDictionary_toCSV(spliceContents, keywords):

    inputkeywords = keywords[0]
    outputkeywords = keywords[1]
    dic = spliceContents [0]
    room_or_zone = spliceContents[1]


    if room_or_zone: 
        fileName = 'Room Load Summary.csv'
        del outputkeywords[1]
        header = ','.join(outputkeywords)
    else: 
        fileName = 'Zone Load Summary.csv'
        del outputkeywords[0]
        header = ','.join(outputkeywords)

    out_path = os.path.join(os.path.dirname(__file__), fileName)    # file to write output data
    with open(out_path, 'w') as out_file:
        out_file.write(header + "\n")
        for key in dic: # for every room in the dictionary write its data to the output file
            file_string = ""
            file_string += (str(key) + ",")
            for pos in range(1, len(outputkeywords)):
                keyword = outputkeywords[pos]
                file_string += (str(dic[key][keyword]) + ",")

            out_file.write(f"{file_string}\n")

# def spliceData(): # puts the data into a dictinary
#  
#     for line in content:
# 
        
#         if "Internal Floor" in line:   # find the floor area
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Internal Floor" not in data[count] :
#                 count += 1
#             area = data[count+1]
#             try:
#                 area = float(area)
#             except:
#                 try:
#                     area = float((area + data[count+2]).strip('\n').strip('"'))
#                 except:
#                     area = "python error"
#             allDataByArea[currentArea]['Floor Area'] = area

#         if "No People(max)" in line:    # find the number of people
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "No People(max)" not in data[count] :
#                 count += 1
#             people = data[count+1]
#             try:
#                 people = float(people)
#             except:
#                 try:
#                     people = float((people + data[count+2]).strip('\n').strip('"'))
#                 except:
#                     people = "python error"
#             if isinstance(people, float) > allDataByArea[currentArea]['Number of People']:
#                 allDataByArea[currentArea]['Number of People'] = people
        
#         if "Cooling tons" in line:      # find the cooling tones
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Cooling tons" not in data[count] :
#                 count += 1
#             cooling = data[count+1]
#             allDataByArea[currentArea]['Cooling Tons'] = float(cooling)

#         if "Main Fan cfm" in line and Cooling_CFM_bool:     # Find the cooling CFM
#             Cooling_CFM_bool = False
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Main Fan cfm" not in data[count] :
#                 count += 1
#             cfm = data[count+1]
#             try:
#                 cfm = float(cfm)
#             except:
#                 try:
#                     cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
#                 except:
#                     cfm = "python error"
#             allDataByArea[currentArea]['Cooling CFM'] = cfm
#         if "Main Fan cfm" in line:      # Find the heating CFM
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Main Fan cfm" not in data[count] :
#                 count += 1
#             cfm = data[count+1]
#             try:
#                 cfm = float(cfm)
#             except:
#                 try:
#                     cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
#                 except:
#                     cfm = "python error"
#             allDataByArea[currentArea]['Heating CFM'] = cfm


#         if "Calculated Ventilation cfm" in line:        # Find the calculated vent CFM
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Calculated Ventilation cfm" not in data[count] :
#                 count += 1
#             cfm = data[count+1]
#             try:
#                 cfm = float(cfm)
#             except:
#                 if not cfm == 'N/A':
#                     try:
#                         cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
#                     except:
#                         cfm = "python error"
#             if  isinstance(cfm, float) and cfm > allDataByArea[currentArea]['Calculated Ventilation CFM']:
#                 allDataByArea[currentArea]['Calculated Ventilation CFM'] = cfm

                
#         if "Input Ventilation cfm" in line:        # Find the inital vent CFM
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Input Ventilation cfm" not in data[count] :
#                 count += 1
#             cfm = data[count+1]
#             try:
#                 cfm = float(cfm)
#             except:
#                 if not cfm == 'N/A':
#                     try:
#                         cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
#                     except:
#                         cfm = "python error"

#             if isinstance(cfm, float) and cfm > allDataByArea[currentArea]['Input Ventilation CFM']:
#                 allDataByArea[currentArea]['Input Ventilation CFM'] = cfm
#         if "Volume" in line:        # Find the room volume
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             while "Volume" not in data[count] :
#                 count += 1
#             volume = data[count+1]
#             try:
#                 volume = float(volume)
#             except:
#                 try:
#                     volume = float((volume + data[count+2]).strip('\n').strip('"'))
#                 except:
#                     volume = "python error"
#             allDataByArea[currentArea]['Volume'] = volume

#         if "Grand Total" in line:       # get all of the cooling and heating information (load, sensible, latebt, ect...)
#             data = line.split(",")
#             data = list(filter(None, data))
#             count = 0
#             # get the cooling data
#             while "Grand Total" not in data[count] :
#                 count += 1
            
#             # the try and excepts are for if the number is >= 1000 trace puts " " around the numbers
#             # this allows us to get the whole number insted of just the first half of the number
#             count += 1
#             InstantSensibleCooling = data[count]
#             try:
#                 InstantSensibleCooling = float(InstantSensibleCooling)
#             except:
#                 count+=1
#                 InstantSensibleCooling = float((InstantSensibleCooling + data[count]).strip('\n').strip('"'))

#             count+=1
#             DelaySensibleCooling = data[count]
#             try:
#                 DelaySensibleCooling = float(DelaySensibleCooling)
#             except:
#                 count+=1
#                 DelaySensibleCooling = float((DelaySensibleCooling + data[count]).strip('\n').strip('"'))
                
#             count+=1
#             LatentCooling = data[count]
#             try:
#                 LatentCooling = float(LatentCooling)
#             except:
#                 count+=1
#                 LatentCooling = float((LatentCooling + data[count]).strip('\n').strip('"'))

#             count+=1
#             coolingBTU = data[count]
#             try:
#                 coolingBTU = float(coolingBTU)
#             except:
#                 count+=1
#                 coolingBTU = float((coolingBTU + data[count]).strip('\n').strip('"'))


#             #get the heating data
#             while "Grand Total" not in data[count]:
#                 count += 1

#             count += 1
#             InstantSensibleHeating = data[count]
#             try:
#                 InstantSensibleHeating = float(InstantSensibleHeating)
#             except:
#                 count+=1
#                 InstantSensibleHeating = float((InstantSensibleHeating + data[count]).strip('\n').strip('"'))

#             count+=1
#             DelaySensibleHeating = data[count]
#             try:
#                 DelaySensibleHeating = float(DelaySensibleHeating)
#             except:
#                 count+=1
#                 DelaySensibleHeating = float((DelaySensibleHeating + data[count]).strip('\n').strip('"'))

#             count+=1
#             LatentHeating = data[count]
#             try:
#                 LatentHeating = float(LatentHeating)
#             except:
#                 count+=1
#                 LatentHeating = float((LatentHeating + data[count]).strip('\n').strip('"'))

#             count+=1
#             heatingBTU = data[count]
#             try:
#                 heatingBTU = float(heatingBTU)
#             except:
#                 count+=1
#                 heatingBTU = float((heatingBTU + data[count]).strip('\n').strip('"'))

#             # add all of the data into the dictionary
#             allDataByArea[currentArea]['Instant Sensible Cooling'] = InstantSensibleCooling
#             allDataByArea[currentArea]['Delay Sensible Cooling'] = DelaySensibleCooling
#             allDataByArea[currentArea]['Latent Cooling'] = LatentCooling
#             allDataByArea[currentArea]['Instant Sensible Heating'] = InstantSensibleHeating
#             allDataByArea[currentArea]['Delay Sensible Heating'] = DelaySensibleHeating
#             allDataByArea[currentArea]['Latent Heating'] = LatentHeating
#             allDataByArea[currentArea]['Total Cooling Load'] = coolingBTU
#             allDataByArea[currentArea]['Total Heating Load'] = heatingBTU

#     return (allDataByArea, room_or_zone_file)    #return tuple with data dictionary and file type bool


# # execute the code
keywords = getKeyWords()
data = spliceData(keywords,readData())
print(data)
dataDictionary_toCSV(data, keywords)
print("Done")
