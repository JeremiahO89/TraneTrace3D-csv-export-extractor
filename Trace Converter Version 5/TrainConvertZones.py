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
    allDataByRoom = {}
    currentRoom = None
    for line in content:
        if "ZONE_" in line: # find the room names
            data = line.split(",")
            room = data[0][5:]
            allDataByRoom[room] = {'Floor Area': 0,'Volume':0, 'Number of People': 0, 'Calculated Ventilation CFM':0, 'Input Ventilation CFM':0, 'Cooling Tons':0,'Cooling CFM':0, 'Total Cooling Load':0, 'Instant Sensible Cooling':0, 'Delay Sensible Cooling':0, 'Latent Cooling': 0, 'Heating CFM':0, 'Total Heating Load':0, 'Instant Sensible Heating':0, 'Delay Sensible Heating':0, 'Latent Heating': 0}
            currentRoom = room
            Cooling_CFM_bool = True 
        
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
                

            allDataByRoom[currentRoom]['Floor Area'] = area
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
            if people > allDataByRoom[currentRoom]['Number of People']:
                allDataByRoom[currentRoom]['Number of People'] = people
        if "Cooling tons" in line:      # find the cooling tones
            data = line.split(",")
            data = list(filter(None, data))
            count = 0
            while "Cooling tons" not in data[count] :
                count += 1
            cooling = data[count+1]
            allDataByRoom[currentRoom]['Cooling Tons'] = float(cooling)



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
            allDataByRoom[currentRoom]['Cooling CFM'] = cfm
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
            allDataByRoom[currentRoom]['Heating CFM'] = cfm


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
            if cfm > allDataByRoom[currentRoom]['Calculated Ventilation CFM']:
                allDataByRoom[currentRoom]['Calculated Ventilation CFM'] = cfm
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
            if cfm > allDataByRoom[currentRoom]['Input Ventilation CFM']:
                allDataByRoom[currentRoom]['Input Ventilation CFM'] = cfm
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
            allDataByRoom[currentRoom]['Volume'] = volume

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
            allDataByRoom[currentRoom]['Instant Sensible Cooling'] = InstantSensibleCooling
            allDataByRoom[currentRoom]['Delay Sensible Cooling'] = DelaySensibleCooling
            allDataByRoom[currentRoom]['Latent Cooling'] = LatentCooling
            allDataByRoom[currentRoom]['Instant Sensible Heating'] = InstantSensibleHeating
            allDataByRoom[currentRoom]['Delay Sensible Heating'] = DelaySensibleHeating
            allDataByRoom[currentRoom]['Latent Heating'] = LatentHeating
            allDataByRoom[currentRoom]['Total Cooling Load'] = coolingBTU
            allDataByRoom[currentRoom]['Total Heating Load'] = heatingBTU

    return allDataByRoom    #return the dictionary with the data in it

def dataDictionary_toCSV(dic):      # takes the dictionary and puts it in a CSV File
    out_path = os.path.join(os.path.dirname(__file__), 'Zone Load Summary.csv')        # writes the data to a file named 'Output.csv'
    with open(out_path, 'w') as out_file:
        out_file.write("Zone,Floor Area,Volume,Number of People,Calculated Ventilation CFM,Input Ventilation CFM,Coling Tons, Cooling CFM,Total Cooling Load (Btu/h),Instant Sensible Cooling,Delay Sensible Cooling,Latent Cooling,Heating CFM,Total Heating Load (Btu/h),Instant Sensible Heating,Delay Sensible Heating,Latent Heating\n")
        for key in dic: # for every room in the dictionary write its data to the output file
            out_file.write(f"{key},{dic[key]["Floor Area"]},{dic[key]["Volume"]},{dic[key]["Number of People"]},{dic[key]["Calculated Ventilation CFM"]},{dic[key]["Input Ventilation CFM"]},{dic[key]["Cooling Tons"]},{dic[key]["Cooling CFM"]},{dic[key]["Total Cooling Load"]},{dic[key]["Instant Sensible Cooling"]},{dic[key]["Delay Sensible Cooling"]},{dic[key]["Latent Cooling"]},{dic[key]["Heating CFM"]},{dic[key]["Total Heating Load"]},{dic[key]["Instant Sensible Heating"]},{dic[key]["Delay Sensible Heating"]},{dic[key]["Latent Heating"]}\n")


dataDictionary_toCSV(spliceData())
print("Done")