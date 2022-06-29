import numpy as np
import os

# defining the folder name where we have the result files
def path_definition(direction):
    global path_data_ratescan
    path_data_ratescan = direction 

# function where we create the folders
def create_folders():

    if not os.path.exists('temp'):                                # temporal archives folder
        os.makedirs('temp')
    if not os.path.exists('output'):                              # folder with all the output data
        os.makedirs('output')  
        
# function to define some parameters for the cases we have L1 and L0
def l0l1params(data_type):
    
    if data_type == 'l1':
        m , n = 2 , 2                                             # dimension of the image tables for each cluster/pixel
        clusOrPx_name = 'Cluster'                                 # name we use for labeling, clusters/pixels

    elif data_type == 'l0':
        m , n = 2 , 2
        clusOrPx_name = 'Pixel'
        
    return m, n, clusOrPx_name
    
# select all the data of l0 or l0, complete function
# we can choose to extract l1 defoult or external arrays
# for the external arrays we jus need to set l1_type='ext'
def select(f_class, l1_type = 'def'):
    
    # extract all the data
    ranges  = ext_ranges()
    classes = ext_class()
    extra   = ext_extra()
    data    = ext_data()
    date    = ext_date()
    
    # s ave the index of the clases we DON'T want
    index = []
    for i in range(len(classes)):
        if classes[i] != f_class:                                # we exclude L1 or L0
            index.append(i)

    # we delete the indexes of the files that we ar not interested in
    data   = [data[ii]   for ii in range(len(data))   if ii not in index]
    date   = [date[ii]   for ii in range(len(date))   if ii not in index]
    ranges = [ranges[ii] for ii in range(len(ranges)) if ii not in index]
    
    if data == []:
        print('ERROR no data found with the requested parameters. Check data.txt and scan_results folder')
    
    # for class 'l1' we add more options
    if (f_class == 'l1') and (l1_type != 'all'):
        
        # iteration in all files
        for i in range(len(data)):
            all_index = range(len(data[i]))
            index     = []

            if l1_type == 'ext':                                 # we extract for the external data the even array index
                for number in all_index:
                    if number%2 == 0:
                        index.append(number)
                        
            if l1_type == 'def':                                 # we extract for the default data te odd array index
                for number in all_index:
                    if number%2 == 1:
                        index.append(number)

            # deleting the indexes selected
            data[i] = [data[i][ii] for ii in all_index if ii not in index]             


    # vector with all data we want putted in 'data.txt'
    extra_dates               = []
    extra_voltage  ,voltage   = [],[]
    extra_dac      ,dac       = [],[]
    extra_neighbour,neighbour = [],[]
    extra_gain     ,gain      = [],[]
    for i in range(len(extra)):
        extra_dates.append(    extra[i][0])
        extra_voltage.append(  extra[i][1])
        extra_dac.append(      extra[i][2])
        extra_neighbour.append(extra[i][3])
        extra_gain.append(     extra[i][4])
    
    
    
    index = []
    for i in range(len(data)):
        if date[i] not in extra_dates:
            index.append(i)
        else:
            voltage.append(  extra[extra_dates.index(date[i])][1])
            dac.append(      extra[extra_dates.index(date[i])][2])
            neighbour.append(extra[extra_dates.index(date[i])][3])
            gain.append(     extra[extra_dates.index(date[i])][4])
            
    # we delete the indexes of the files that we ar not interested in
    data   = [data[ii]   for ii in range(len(data))   if ii not in index]
    date   = [date[ii]   for ii in range(len(date))   if ii not in index]
    ranges = [ranges[ii] for ii in range(len(ranges)) if ii not in index]            
            
    return data, date, ranges, voltage, gain, dac, neighbour
        
# extract all data from a document
def ext_data():
    os.chdir(path_data_ratescan) # entering the folder
    files, data,jj = [], [], 0
    
    #reading all documents
    for name in os.listdir(): 
        if name.endswith('.result'):                # we filter the documents with termination .result
            files.append(open(name, "r").read(-1))  # read
    
    #extracting the vectors of data
    for k in range(len(files)):        
        data_sub,flag, jj=[], False, 0 # temporal array for save the data, and marker for wen we are inside a vector
        
        #loop of all the document
        for i in range(len(files[k])): 
               
            if (flag == False) and (files[k][i] == '['):  # detect the start of an array
                flag, temp = True, '['                
            elif (flag == True) and (files[k][i] != ']'): # save the contect inside an array
                temp = temp + files[k][i]
            elif (flag == True) and (files[k][i] == ']'): # detect the end of the array
                temp, flag = temp + ']', False
                data_sub.append(np.fromstring(temp[1:-1], dtype=int, sep=',')) # convert the string to array form
        data.append(data_sub)
        
    os.chdir('..')  # back to the main folder
    return data     # data in array form

# extract the date of the files for labeling
def ext_date():
    os.chdir(path_data_ratescan)
    
    # extracting all file names
    file_names, dates = [], []
    for file_total in os.listdir(): 
        if file_total.endswith('.result'):    # we filter the documents with termination .result
            file_names.append(file_total)
            
    # iterating trough the names for extract the date
    for name in file_names:  
        data_sub, flag = [], False 
        
        # loop of all doc names
        for i in range(len(name)):            
            if (flag == False) and (name[i] == '.'):  # detect the start of date
                flag, temp = True, ''                
            elif (flag == True) and (name[i] != '.'): # save the content  
                temp=temp+name[i]
            elif (flag == True) and (name[i] == '.'): # detect the end of the date
                flag = False
                dates.append(temp)     
                
    os.chdir('..')
    return dates # return the dates

# extract the ranges form the files
def ext_ranges():
    os.chdir(path_data_ratescan) # entering the folder
    files = []

    # reading all documents
    for name in os.listdir(): 
        if name.endswith('.result'):                # we filter the documents with termination .result
            files.append(open(name, "r").read(-1))  # read

    # extracting data
    ranges = []
    for k in range(len(files)):  
        r     = []
        begin = files[k].find('Begin:')
        end   = files[k].find('End:')
        steps = files[k].find('Steps:')
        r.append(int(files[k][begin+7:begin+10].replace('-','').replace(' ','')))
        r.append(int(files[k][end+4:end+9].replace(     '-','').replace(' ','').replace('S','')))
        r.append(int(files[k][steps+7:steps+8].replace( '-','').replace(' ','')))
        ranges.append(r)
    
        
    os.chdir('..') # back to the main folder
    return ranges  # data in array form 

# extract a list with the class of data
def ext_class():
    os.chdir(path_data_ratescan)
    
    # fextraction of the file names
    file_names = []
    for file_total in os.listdir(): 
        if file_total.endswith('.result'):   # filter the documents with termination .result
            file_names.append(file_total)
            
    # classification l0-l1 depending of the file name
    file_class = []
    for name in file_names:
        if name.startswith('scan_ipr'):
            file_class.append('l0')
        elif name.startswith('scan_l1'):
            file_class.append('l1')
            
    os.chdir('..')
    return file_class   # we return an array with the information for a vector if is 'l0' or 'l1'

def ext_extra():
    
    with open('extra_data.txt') as file:
        lines = file.readlines()
    for i in range(len(lines)):
        if i != len(lines)-1:
            lines[i] = lines[i].replace('\n','') # .replace(':','_')
            lines[i] = lines[i].split(',')
            if lines[i][-1].replace(' ','').replace('-','') == '':
                lines[i][-1] = 0
            else:
                lines[i][-1] = int(lines[i][-1].replace(' ','').replace('-',''))
                
            lines[i]=[lines[i][0], lines[i][1], lines[i][-3], lines[i][-2], lines[i][-1]]
        elif lines[i] == '\n':
            lines.pop(-1)
        else:
            lines[i] = lines[i].replace('\n','') # .replace(':','_')
            lines[i] = lines[i].split(',')
            if lines[i][-1].replace(' ','').replace('-','') == '':
                lines[i][-1] = 0
            else:
                lines[i][-1] = int(lines[i][-1].replace(' ','').replace('-',''))
            lines[i] = [lines[i][0],lines[i][1],lines[i][-3],lines[i][-2],lines[i][-1]]
            
    return lines        
        
    
# fix data with periodic noise with the form 010101010 --> 00000
def fix_noise(x, data):
    
    X = x.copy()
    Y = data.copy()
    
    for periodicity in [2,5]:
        # find noise pattern
        indexStart = ''
        if periodicity == 2:
            for i in range(len(Y)-7):
                if  (Y[i] >= 100) and (Y[i+1] == 0)   and (Y[i+2] >= 100) and (Y[i+3] == 0) and (Y[i+4] >= 100)
                and (Y[i+5] == 0) and (Y[i+6] >= 100) and (Y[i+7] == 0):
                    
                    indexStart = i
                    break
                    
        elif (periodicity == 5):
            for i in range(len(Y)-11):
                if  (Y[i] >= 100) and (Y[i+1] == 0) and (Y[i+2] == 0) and (Y[i+3] == 0) and (Y[i+4] == 0)    and (Y[i+5] >= 100)
                and (Y[i+6] == 0) and (Y[i+7] == 0) and (Y[i+8] == 0) and (Y[i+9] == 0) and (Y[i+10] >= 100) and (Y[i+11] == 0):
                    
                    indexStart = i
                    break

        # if we dont find a noise pattern       
        if indexStart != '':
            index = []
            for i in range(len(Y)):
                if i%periodicity == indexStart%periodicity:
                    index.append(i)

            X = [X[ii] for ii in range(len(X)) if ii not in index]
            Y = [Y[ii] for ii in range(len(Y)) if ii not in index]            
    
    return X, Y        


'''
# not used functions
# remove the zero vectors at extracting
def filter_zero(data):
    data_changed = data,copy()
    
    # iterate trough the data to find if an array have elements != 0
    for i in range(len(data)):
        index = []
        for j in range(len(data[i])):
            zeros = True
            
            for k in range(len(data[i][j])):
                if data[i][j][k] != 0: # detect non zero elements
                    zeros = False
            
            # save the indexes to delete them at the end of the loop
            if zeros == True:
                index.append(j)
                
        # deleting the indexes that correspond to zeros
        data_changed[i] = [data[i][ii] for ii in range(len(data[i])) if ii not in index]
    
    # if all arrays in a file are zero, we set the file as a unique array [0,0] that can be 
    # distinguished from the other files, in order to respect the labeling we can just delete this files
    index = []
    for i in range(len(data)):
        if data_changed[i] == []:
            data_changed[i].append([0,0])
        
    return data_changed # return the data arrays without full zeros

# instead of removing zero vector, we can turn it to empty arrays 
# for when we are interested in some information of detemined clusters
def empty_zero(data):
    data_changed = data.copy()
    
    # iterating trough all arrays
    for i in range(len(data)):
        index = []
        for j in range(len(data[i])):
            zeros = True
            
            for k in range(len(data[i][j])):
                if data[i][j][k] != 0: # finding non zero elements
                    zeros = False
                  
            if zeros == True: # save the index 
                index.append(j)
                
        for ii in index: # convert this arrays to empty arrays
            data_changed[i][ii] = []
            
    return data_changed   
'''
