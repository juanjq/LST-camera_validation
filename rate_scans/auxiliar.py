import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np

from scipy.optimize import curve_fit
from scipy.optimize import root
from scipy.stats    import norm
from PyPDF2         import PdfFileMerger 


# step function to fit
def R(DT, a, b):
    return 1000 * (1-1/(1 + np.e**(-a*(DT-b)))) 


# fitting function
# ranges --> X coordinates
# data   --> Y coordinates
def fitting(ranges, data):

    # we copy this data
    X     = ranges.copy()
    Y, Yc =   data.copy(), data.copy()     # Yc is a array we wil do some changes for finding optimal parameters
    
    # we define some flags for different cases we have
    allZeros     = True     # if the initial array are composed at all of zeros (or high values)
    notNearIndex = False    # if we dont have any very near to 1000 value
    noSolution   = False    # if the system have not solution (fitting = 0)
    
    # testing if all are ~zeros (or high values)
    for j in range(len(Yc)):
        
        if Yc[j] <= 1010 and Yc[j] >= 50:  # we search for a non ~zero value
            allZeros = False 
            break
            
    if allZeros == True:                   # in case of being zeros we will have a zero function
        params = [10e10, -10]
        
    else:
         
        # if we have almost one element between 1010 and 50, we start to looking for its validity
        # first of all we search for all the VERY NEAR points (between 1010-990) and add them to a list
        
        near_i = []                        # array with all the VERY NEAR points
        index_start = 0                    # index that before it, we will not take into account any point (def = 0)
        
        for i in range(len(Yc)):
            if Yc[i] < 1010 and Yc[i] > 990:
                near_i.append(i)
            
        # we check if this indexes are valid (if they are a plateau or only random points) 
        # to be specific we search for the first of them that is valid
        for i in near_i:
            
            # for being valid we look if points are near between them 
            if i == 0:
                if (abs(Yc[i] - Yc[i+1]) < 10):  
                    index_start = i
                    break         
            else:
                if (abs(Yc[i] - Yc[i-1]) < 20 or abs(Yc[i] - Yc[i+1]) < 50):  
                    index_start = i
                    break         
                    
            if i == near_i[-1]:                            # if we arrive to last index --> no near points
                notNearIndex = True
                break
               

        
        # in the case they are random points notNearIndex=True, we will search 
        # for a decay between 1000 and 0 starting from nearest points to 1000
        if notNearIndex == True or near_i == []:  
            
            # find initial closer element to 1000 excludin both first and second index
            Yc[0] = 0
            Yc[1] = 0
            close_i = closer_element_index(Yc, 1000)       # function to find the closer element index of an array
            
            if close_i == 0 or close_i == 1:               # if the closer element are 0, (as we def) will be no solution
                noSolution = True
                
            else:
                # conditions to NOT be a good start point, (IMPOSING DECAY)
                while data[close_i+1] > data[close_i] or data[close_i] > data[close_i-1] or data[close_i] > data[close_i-2]:

                    # if the closer point is ~zero, we can say that there is no solution
                    if (data[close_i] < 20) or (close_i == 0):
                        noSolution = True
                        break

                    # if index not valid making the closer index--> 0, and searching for the next closer index
                    close_i,Yc = next_closer(Yc, 1000, close_i)

            index_start = close_i                         # we define a index that before the point will not be used
            
        # the case with noSolution = True, will fit with a zero function
        if noSolution == True:
            params = [10e10,-10]
            
        # the other cases where we found a valid start point we truncate the arrays
        else:
            Y = Y[index_start:]
            X = X[index_start:] 
            
            # upper filtering - we filter too much high points
            index = []                   
            for i in range(len(Y)):
                if Y[i] >= 1010:                         # we only mantain the points lower than 1010
                    index.append(i)
                    
            X = [X[ii] for ii in range(len(X)) if ii not in index]
            Y = [Y[ii] for ii in range(len(Y)) if ii not in index]
            
            # filter big jumps - we filter random or points with big jumps
            index = []                   
            for i in range(len(Y)-1):
                if Y[i+1] - Y[i] > 50:                   # diference into one point and the following higher than 50
                    index.append(i+1)          

            X = [X[ii] for ii in range(len(X)) if ii not in index]
            Y = [Y[ii] for ii in range(len(Y)) if ii not in index]
            
            # now we fit to the function R
            # first of all we will find a good start point 'b'
            indexUP   = None
            indexDOWN = None
            
            for i in range(len(X)):                      # we search for the last point around 1000
                
                if Y[i] < 1010 and Y[i] > 970:           # around 1000 points
                    indexUP = i
                    
            if indexUP == None:                          # if not very near 1000, we set it as the first point
                indexUP = 0
                
            for i in range(len(X)):                      # we search for the first point around 0
                
                if Y[i] < 50:                            # around zero first point
                    indexDOWN = i
                    break
                    
            b0 = X[indexUP] + (X[indexDOWN] - X[indexUP]) / 2  # b0 will be the mean point between the start and end
            
            # we add a try and except barrier for the cases that for same reason return an error when fitting
            # in that cases we will fit the function to zero            
            try:
                params,other=curve_fit(R, X, Y, p0 = [1, b0], maxfev = 50000)

            except:
                params = [10e10, -10]                    # zero fitting
                
    return params[0], params[1], X, Y                    # return of the parameters of R(a,b) 
                                                         # and X,Y the arrays used when passing the filtering


#function to find the closer element index to a value in a array
def closer_element_index(array, value):
    array = np.asarray(array)
    idx   = (np.abs(array - value)).argmin()
    return idx

#function to find the second closer element index, giving the index of the closer
def next_closer(array, value, before_index):
    array[before_index] = 0
    array = np.asarray(array)
    idx   = (np.abs(array - value)).argmin()
    return idx, array                                    #reduced array (closer index ---> 0)


#treshold tratment, we input the full treshol array and we return other arrays that will be usefull
def treshold_tr(treshold, run_failed):
    
    #treshold treatment######################################
    # tresholdRaw     = All data without failed cases
    # tresholdMean    = Data with failed cases --> mu value                  (for camera left plot )
    # tresholdZero    = Data with failed cases --> 0                         (for each cluster plot)
    # tresholdFitting = Array with failed clusters = 1, and fitted ones = 0  (for camera right plot)
    # treshold_dev    = Array with the deviation from the treshold
    
    tresholdRaw     = treshold.copy()
    tresholdMean    = treshold.copy()
    tresholdZero    = treshold.copy()
    tresholdFitting = np.zeros(len(treshold))
    treshold_dev    = []


    Nzeros = 0                                           #number of non fitted clusters/pixels
    index  = []
    for i in range(len(treshold)):                       #array with indexes of non fitted ones
        if treshold[i] == None:
            Nzeros = Nzeros + 1
            index.append(i)

    tresholdRaw = [tresholdRaw[ii] for ii in range(len(tresholdRaw)) if ii not in index]        

    # gaussian fitting
    # with tresholdRaw (only taking into account the non failed clusters) we calculate the mean value and the sigma
    (mean, sigma) = norm.fit(tresholdRaw)
    
    for i in range(len(treshold)):
        if i not in index:
            treshold_dev.append(treshold[i]-mean)
        if i in index:
            treshold_dev.append(None)

    # now we change the arrays in the way we need to change the non fitted values
    for i in index:
        tresholdMean[i]    = mean
        tresholdZero[i]    = 0
        tresholdFitting[i] = 1

    # we return the different treshold arrays, the number of zeros, the mean value, and the sigma
    return tresholdRaw, tresholdMean, tresholdZero, tresholdFitting, treshold_dev, Nzeros, mean, sigma


#function for repairing pdfs (python dont save perfectly the pdfs, 
#so for merging them we will have to repair them before)
def repair_pdf(file_name):
    EOF_MARKER = b'%%EOF'                                #we look for the EOF marker that is the 'End' of the actual pdf

    with open(file_name, 'rb') as f:                     #reading the pdf
        contents = f.read()

    # check if EOF is somewhere else in the file
    if EOF_MARKER in contents:
        # we can remove the early %%EOF and put it at the end of the file
        contents = contents.replace(EOF_MARKER, b'')
        contents = contents + EOF_MARKER
    else:
        contents = contents[:-6] + EOF_MARKER

    #replacing the file with same name ended by '_r'
    with open(file_name.replace('.pdf', '') + '_r.pdf', 'wb') as f:
        f.write(contents)
        
#function to merge a list of pdfs, giving the name files of them     
def merge_pdf(pdf_order, run, data_type, gain, date, neigh, voltage, dac, run_failed, plot_camera, plot_run):

    if plot_run == True and run_failed == False :         #we only do it if we want to plot the runs
        
        pdfs = []                                         #pdf names after repair
        for i in range(len(pdf_order)):
            if plot_camera != False or pdf_order[i] != 'temp/camera_plot.pdf':
            
                pdfs.append(pdf_order[i].replace('.pdf', '_r.pdf'))

        # repairing all of the pdfs
        for i in range(len(pdf_order)):
            repair_pdf(pdf_order[i])
            
        # merging pdfs
        merger = PdfFileMerger()
        for pdf in pdf_order:
            merger.append(pdf)
            
        # name of the merged pdf
        filename = 'output/' + data_type + '_' + 'gain' + str(gain[run]) + '_'
        filename = filename  + 'neigh' + neigh[run].replace(' ', '') + '_' + 'dac' + dac[run].replace(' ', '') + '_'
        filename = filename  + voltage[run].replace(' ', '').replace('_', '') + '_' + date[run] + '.pdf'
        merger.write(filename) # name of final file

        merger.close()  
        
    elif plot_run == True and run_failed == True :        # we only do it if we want to plot the runs
        
        pdfs = []                                         # pdf names after repair
        for i in range(len(pdf_order)):
            if pdf_order[i] == 'temp/multi_graphs.pdf':
                pdfs.append(pdf_order[i].replace('.pdf', '_r.pdf'))

        # repairing all of the pdfs
        for i in range(len(pdf_order)):
            repair_pdf(pdf_order[i])
            
        # merging pdfs
        merger = PdfFileMerger()
        for pdf in pdfs:
            merger.append(pdf)
            
        # name of the merged pdf
        filename = 'output/'+ data_type + '_' + 'gain' + str(gain[run]) + '_'
        filename = filename + 'neigh' + neigh[run].replace(' ', '') + '_' + 'dac' + dac[run].replace(' ','') + '_'
        filename = filename + voltage[run].replace(' ', '').replace('_', '') + '_' + date[run] + '.pdf'
        merger.write(filename) #name of final file

        merger.close()     

# function to merge a list of pdfs of the TOTAL analysis     
def merge_pdfTOT(pdf_order, data_type, plot_camera, plot_run, data1run, voltageName):

    if data1run == False :         # we only do it if we want to plot the runs
        
        pdfs = []                  # pdf names after repair
        for i in range(len(pdf_order)):
            if plot_camera != False or pdf_order[i] != 'temp/camera_total.pdf':
            
                pdfs.append(pdf_order[i].replace('.pdf', '_r.pdf'))

        #repairing all of the pdfs
        for i in range(len(pdf_order)):
            repair_pdf(pdf_order[i])
            
        # merging pdfs
        merger = PdfFileMerger()
        for pdf in pdf_order:
            merger.append(pdf)
            
        # name of the merged pdf
        merger.write('output/complete_analysis_' + data_type + '_' + voltageName + '.pdf')   #name of final file

        merger.close()  
        
        
#matplotlib parameters used to do the plots
def parameters(n=6):
    plt.rcParams['mathtext.rm']         = 'Bitstream Vera Sans'
    plt.rcParams['mathtext.it']         = 'Bitstream Vera Sans:italic'
    plt.rcParams['mathtext.bf']         = 'Bitstream Vera Sans:bold'
    plt.rcParams['mathtext.fontset']    = 'stix'
    plt.rcParams['figure.dpi']          = 200
    plt.rcParams['savefig.dpi']         = 200
    plt.rcParams['savefig.transparent'] = True
    plt.rcParams['axes.prop_cycle']     = plt.cycler(color=[
        'darkblue','darkviolet','deeppink','crimson','orangered','darkorange','sandybrown','gold','yellow'])
    plt.rcParams.update({"font.size": n})
