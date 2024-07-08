import os, csv

def spliceData(): # puts the data into a dictinary

    # get the .csv file from the current folder
    filename = "none"
    for names in os.listdir(os.path.dirname(__file__)):
        if ".csv" in names:
            filename = names

    # check to see if it found the folder
    if ".csv" not in filename:
        out_path = os.path.join(os.path.dirname(__file__), 'Python Error Report.txt')
        with open(out_path, 'w') as out_file:
            out_file.write("No Valid File In the Folder:  \n")
            out_file.write(str(os.path.dirname(__file__)) + "\n")
            out_file.write("List of the Files in this folder  \n\n")
            out_file.write(str(os.listdir(os.path.dirname(__file__))))

    # open and read the file
    target_path = os.path.join(os.path.dirname(__file__), filename)
    with open(target_path, "r") as the_file:
        content = the_file.readlines()

    #get all of the data from the file
    allDataByArea = {}  # dict to store the data
    currentArea= None   # string with current spot in allDataByArea
    room_or_zone_file = False # bool for output to either be for room file (False) or zones file (True)

    
    for line in content:
        if "ROOM_" in line or "ZONE_" in line: # find the area name
            data = line.split(",")
            area = data[0][5:]
            allDataByArea[area] = {'Floor Area': 0,'Volume':0, 'Number of People': 0, 'Calculated Ventilation CFM':0, 'Input Ventilation CFM':0, 'Cooling Tons':0,'Cooling CFM':0, 'Total Cooling Load':0, 'Instant Sensible Cooling':0, 'Delay Sensible Cooling':0, 'Latent Cooling': 0, 'Heating CFM':0, 'Total Heating Load':0, 'Instant Sensible Heating':0, 'Delay Sensible Heating':0, 'Latent Heating': 0}
            currentArea = area
            Cooling_CFM_bool = True 

            if "ZONE_" in line: # set the output file print type
                room_or_zone_file = True
        
        if "Internal Floor" in line:   # find the floor area
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Internal Floor" not in data[count] :
                count += 1
            area = data[count+1]
            try:
                area = float(area)
            except:
                try:
                    area = float((area + data[count+2]).strip('\n').strip('"'))
                except:
                    area = "python error"
            allDataByArea[currentArea]['Floor Area'] = area

        if "No People(max)" in line:    # find the number of people
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "No People(max)" not in data[count] :
                count += 1
            people = data[count+1]
            try:
                people = float(people)
            except:
                try:
                    people = float((people + data[count+2]).strip('\n').strip('"'))
                except:
                    people = "python error"
            if isinstance(people, float) > allDataByArea[currentArea]['Number of People']:
                allDataByArea[currentArea]['Number of People'] = people
        
        if "Cooling tons" in line:      # find the cooling tones
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Cooling tons" not in data[count] :
                count += 1
            cooling = data[count+1]
            allDataByArea[currentArea]['Cooling Tons'] = float(cooling)

        if "Main Fan cfm" in line and Cooling_CFM_bool:     # Find the cooling CFM
            Cooling_CFM_bool = False
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Main Fan cfm" not in data[count] :
                count += 1
            cfm = data[count+1]
            try:
                cfm = float(cfm)
            except:
                try:
                    cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
                except:
                    cfm = "python error"
            allDataByArea[currentArea]['Cooling CFM'] = cfm
        if "Main Fan cfm" in line:      # Find the heating CFM
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Main Fan cfm" not in data[count] :
                count += 1
            cfm = data[count+1]
            try:
                cfm = float(cfm)
            except:
                try:
                    cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
                except:
                    cfm = "python error"
            allDataByArea[currentArea]['Heating CFM'] = cfm


        if "Calculated Ventilation cfm" in line:        # Find the calculated vent CFM
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Calculated Ventilation cfm" not in data[count] :
                count += 1
            cfm = data[count+1]
            try:
                cfm = float(cfm)
            except:
                if not cfm == 'N/A':
                    try:
                        cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
                    except:
                        cfm = "python error"
            if  isinstance(cfm, float) and cfm > allDataByArea[currentArea]['Calculated Ventilation CFM']:
                allDataByArea[currentArea]['Calculated Ventilation CFM'] = cfm

                
        if "Input Ventilation cfm" in line:        # Find the inital vent CFM
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Input Ventilation cfm" not in data[count] :
                count += 1
            cfm = data[count+1]
            try:
                cfm = float(cfm)
            except:
                if not cfm == 'N/A':
                    try:
                        cfm = float((cfm + data[count+2]).strip('\n').strip('"'))
                    except:
                        cfm = "python error"

            if isinstance(cfm, float) and cfm > allDataByArea[currentArea]['Input Ventilation CFM']:
                allDataByArea[currentArea]['Input Ventilation CFM'] = cfm
        if "Volume" in line:        # Find the room volume
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Volume" not in data[count] :
                count += 1
            volume = data[count+1]
            try:
                volume = float(volume)
            except:
                try:
                    volume = float((volume + data[count+2]).strip('\n').strip('"'))
                except:
                    volume = "python error"
            allDataByArea[currentArea]['Volume'] = volume

        if "Grand Total" in line:       # get all of the cooling and heating information (load, sensible, latebt, ect...)
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            # get the cooling data
            while "Grand Total" not in data[count] :
                count += 1
            
            # the try and excepts are for if the number is >= 1000 trace puts " " around the numbers
            # this allows us to get the whole number insted of just the first half of the number
            count += 1
            InstantSensibleCooling = data[count]
            try:
                InstantSensibleCooling = float(InstantSensibleCooling)
            except:
                count+=1
                InstantSensibleCooling = float((InstantSensibleCooling + data[count]).strip('\n').strip('"'))

            count+=1
            DelaySensibleCooling = data[count]
            try:
                DelaySensibleCooling = float(DelaySensibleCooling)
            except:
                count+=1
                DelaySensibleCooling = float((DelaySensibleCooling + data[count]).strip('\n').strip('"'))
                
            count+=1
            LatentCooling = data[count]
            try:
                LatentCooling = float(LatentCooling)
            except:
                count+=1
                LatentCooling = float((LatentCooling + data[count]).strip('\n').strip('"'))

            count+=1
            coolingBTU = data[count]
            try:
                coolingBTU = float(coolingBTU)
            except:
                count+=1
                coolingBTU = float((coolingBTU + data[count]).strip('\n').strip('"'))


            #get the heating data
            while "Grand Total" not in data[count]:
                count += 1

            count += 1
            InstantSensibleHeating = data[count]
            try:
                InstantSensibleHeating = float(InstantSensibleHeating)
            except:
                count+=1
                InstantSensibleHeating = float((InstantSensibleHeating + data[count]).strip('\n').strip('"'))

            count+=1
            DelaySensibleHeating = data[count]
            try:
                DelaySensibleHeating = float(DelaySensibleHeating)
            except:
                count+=1
                DelaySensibleHeating = float((DelaySensibleHeating + data[count]).strip('\n').strip('"'))

            count+=1
            LatentHeating = data[count]
            try:
                LatentHeating = float(LatentHeating)
            except:
                count+=1
                LatentHeating = float((LatentHeating + data[count]).strip('\n').strip('"'))

            count+=1
            heatingBTU = data[count]
            try:
                heatingBTU = float(heatingBTU)
            except:
                count+=1
                heatingBTU = float((heatingBTU + data[count]).strip('\n').strip('"'))

            # add all of the data into the dictionary
            allDataByArea[currentArea]['Instant Sensible Cooling'] = InstantSensibleCooling
            allDataByArea[currentArea]['Delay Sensible Cooling'] = DelaySensibleCooling
            allDataByArea[currentArea]['Latent Cooling'] = LatentCooling
            allDataByArea[currentArea]['Instant Sensible Heating'] = InstantSensibleHeating
            allDataByArea[currentArea]['Delay Sensible Heating'] = DelaySensibleHeating
            allDataByArea[currentArea]['Latent Heating'] = LatentHeating
            allDataByArea[currentArea]['Total Cooling Load'] = coolingBTU
            allDataByArea[currentArea]['Total Heating Load'] = heatingBTU

    return (allDataByArea, room_or_zone_file)    #return tuple with data dictionary and file type bool

def dataDictionary_toCSV(content):
    """
    Pre: 
    content -> tuple: pos 0 contains a dict with the data (values) sorted by area name (keys), pos 1 contains a bool True if it was a zone file, False if it was a room file
    """
    dic = content[0]
    csvType = content[1]

    if csvType: 
        fileName = 'Zone Load Summary.csv'
        header = "Zone Name,Floor Area,Volume,Number of People,Calculated Ventilation CFM,Input Ventilation CFM,Coling Tons, Cooling CFM,Total Cooling Load (Btu/h),Instant Sensible Cooling,Delay Sensible Cooling,Latent Cooling,Heating CFM,Total Heating Load (Btu/h),Instant Sensible Heating,Delay Sensible Heating,Latent Heating\n"
    else: 
        fileName = 'Room Load Summary.csv'
        header = "Room Name,Floor Area,Volume,Number of People,Calculated Ventilation CFM,Input Ventilation CFM,Coling Tons, Cooling CFM,Total Cooling Load (Btu/h),Instant Sensible Cooling,Delay Sensible Cooling,Latent Cooling,Heating CFM,Total Heating Load (Btu/h),Instant Sensible Heating,Delay Sensible Heating,Latent Heating\n"

    out_path = os.path.join(os.path.dirname(__file__), fileName)    # file to write output data
    with open(out_path, 'w') as out_file:
        out_file.write(header)
        for key in dic: # for every room in the dictionary write its data to the output file
            out_file.write(f"{key},{dic[key]["Floor Area"]},{dic[key]["Volume"]},{dic[key]["Number of People"]},{dic[key]["Calculated Ventilation CFM"]},{dic[key]["Input Ventilation CFM"]},{dic[key]["Cooling Tons"]},{dic[key]["Cooling CFM"]},{dic[key]["Total Cooling Load"]},{dic[key]["Instant Sensible Cooling"]},{dic[key]["Delay Sensible Cooling"]},{dic[key]["Latent Cooling"]},{dic[key]["Heating CFM"]},{dic[key]["Total Heating Load"]},{dic[key]["Instant Sensible Heating"]},{dic[key]["Delay Sensible Heating"]},{dic[key]["Latent Heating"]}\n")

# execute the code
dataDictionary_toCSV(spliceData())
print("Done")