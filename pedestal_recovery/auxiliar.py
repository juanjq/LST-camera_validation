import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import os
      

####################################################    
# data extraction function
def readPedestalCSV(path):

    print('Reading CSV...')
    df  = pd.read_csv(path)

    pedestal = []
    stdv     = []
    time     = df.iloc[:, 0].to_numpy()
    time     = time - time[0]     # taking as reference the initial time

    for i in range(1855): 
        pedestal.append(df.iloc[:, i * 2 + 1])
        stdv.append(df.iloc[:    , i * 2 + 2])

    del df  # deleting to clean memory
    print('Finished\n')
    
    return pedestal, stdv, time
####################################################



####################################################
# defining a function for binning
def binning(DIV, freq, dt, time, pedestalTotal, stdvTotal):
    # empty array for each bin
    pedestalBins = [[] for b in range(DIV)]
    stdvBins     = [[] for b in range(DIV)]
    dtBins       = [[] for b in range(DIV)]

    # points to do the binning
    bins = np.linspace(0, 1 / freq, DIV + 1)

    # iterating over pixels and events
    for ev in range(len(dt[0])):

        if (ev % 2600 == 0) or (ev == 0):
            print('Binning - ' + str(int(100 * ev / len(time))) + '%...')


        for px in range(1855):        
            # filling the data in corresponding bin
            for b in range(DIV):
                if (dt[px][ev] >= bins[b]) and (dt[px][ev] < bins[b + 1]):

                    pedestalBins[b].append(pedestalTotal[px][ev])
                    stdvBins[b].append(stdvTotal[px][ev])
                    dtBins[b].append(dt[px][ev])
    print('Binning - 100% \n')

    print('Getting mean values...')
    # mean values and standard deviations for each bin
    pedestalBinsMean = [np.mean(pedestalBins[i]) for i in range(len(pedestalBins)) if pedestalBins[i] != []]
    stdvBinsMean     = [np.mean(stdvBins[i])     for i in range(len(stdvBins))     if stdvBins[i]     != []]
    dtBinsMean       = [np.mean(dtBins[i])       for i in range(len(dtBins))       if dtBins[i]       != []]
    pedestalBinsStd  = [np.std(pedestalBins[i])  for i in range(len(pedestalBins)) if pedestalBins[i] != []]
    stdvBinsStd      = [np.std(stdvBins[i])      for i in range(len(stdvBins))     if stdvBins[i]     != []]
    dtBinsStd        = [np.std(dtBins[i])        for i in range(len(dtBins))       if dtBins[i]       != []]         
    print('Finished \n')
    
    return [pedestalBinsMean, pedestalBinsStd], [stdvBinsMean, stdvBinsStd], [dtBinsMean, dtBinsStd]
####################################################



####################################################
# defining a function for binning over pixels
def binningPX(DIV, px, freq, dt, time, pedestalTotal, stdvTotal):
    # empty array for each bin
    pedestalBins = [[] for b in range(DIV)]
    stdvBins     = [[] for b in range(DIV)]
    dtBins       = [[] for b in range(DIV)]

    # points to do the binning
    bins = np.linspace(0, 1 / freq, DIV + 1)

    # iterating over pixels and events
    for ev in range(len(dt[0])):

        if (ev % 11000 == 0) or (ev == 0):
            print('Binning - ' + str(int(100 * ev / len(time))) + '%...')

        for b in range(DIV):
            if (dt[px][ev] >= bins[b]) and (dt[px][ev] < bins[b+1]):

                pedestalBins[b].append(pedestalTotal[px][ev])
                stdvBins[b].append(stdvTotal[px][ev])
                dtBins[b].append(dt[px][ev])
                
    print('Binning - 100% \n')

    print('Getting mean values...')
    # mean values and standard deviations for each bin
    pedestalBinsMean = [np.mean(pedestalBins[i]) for i in range(len(pedestalBins)) if pedestalBins[i] != []]
    stdvBinsMean     = [np.mean(stdvBins[i])     for i in range(len(stdvBins))     if stdvBins[i]     != []]
    dtBinsMean       = [np.mean(dtBins[i])       for i in range(len(dtBins))       if dtBins[i]       != []]
    pedestalBinsStd  = [np.std(pedestalBins[i])  for i in range(len(pedestalBins)) if pedestalBins[i] != []]
    stdvBinsStd      = [np.std(stdvBins[i])      for i in range(len(stdvBins))     if stdvBins[i]     != []]
    dtBinsStd        = [np.std(dtBins[i])        for i in range(len(dtBins))       if dtBins[i]       != []]         
    print('Finished \n')
    
    return [pedestalBinsMean, pedestalBinsStd], [stdvBinsMean, stdvBinsStd], [dtBinsMean, dtBinsStd]
####################################################



####################################################
# function for searching a run in the directories
def search(root, RUN):
    
    date = None   # initially set to None in the cas the run was not found in root
    
    directories = [dirs for dirs in os.listdir(root)]  # list of all the date directories

    for dirs in directories:    # checking over all directories
        path  = os.path.join(root, dirs)

        files = []
        for r, d, f in os.walk(path):
            for file in f:
                files.append(file)     # getting all the filenames

        # we want only the number of run and the number of subrun
        files = [files[i][11:-8].split('.') for i in range(len(files))]
        files = [[int(files[i][j])          for j in range(len(files[i]))] for i in range(len(files))]

        # we eliminate the repeated elements (we have 4 docs for each subrun)
        filesFilter = []
        for i in files:
            if i not in filesFilter:
                filesFilter.append(i)    
        
        runs = [filesFilter[i][0] for i in range(len(filesFilter))] # array with run number

        # checking if our run is in this directory
        if RUN in runs:
            date = dirs

            # subruns finding
            filesRun = [filesFilter[i] for i in range(len(filesFilter)) if filesFilter[i][0] == RUN]
            subruns  = [filesRun[i][1] for i in range(len(filesRun))]
            subruns.sort()
    
    if date == None:
        print('ERROR: Run not found in root')
    else:
        # return the date name and the number of subruns
        return date, subruns
####################################################



####################################################
# function that create the directories if not exist
def create_folder(path):

    # check whether the specified path exists or not
    isExist = os.path.exists(path)

    if not isExist:

      # Create a new directory
      os.makedirs(path)
####################################################



####################################################
# function to find the LST number of camera we are analysing the data
def find_LST_num(root):
    directories = [dirs for dirs in os.listdir(root)]
    path        = os.path.join(root, directories[0]) 

    files = []
    for r, d, f in os.walk(path):
        for file in f:
            files.append(file)     # getting all the filenames

    path  = root + directories[0] + '/' + files[0]
    index = path.find('LST-')

    LST_camera = path[index + 4 : index + 5]
    
    return LST_camera
####################################################



####################################################
# matplotlib parameters
def parameters(n=18):
    plt.rcParams['mathtext.rm']         = 'Bitstream Vera Sans'
    plt.rcParams['mathtext.it']         = 'Bitstream Vera Sans:italic'
    plt.rcParams['mathtext.bf']         = 'Bitstream Vera Sans:bold'
    plt.rcParams['mathtext.fontset']    = 'stix'
    
    plt.rcParams['xtick.major.size']    = 8
    plt.rcParams['ytick.major.size']    = 8
    plt.rcParams['xtick.major.width']   = 1.8
    plt.rcParams['ytick.major.width']   = 1.8   
    
    plt.rcParams['axes.linewidth']      = 1.4
    plt.rcParams['lines.linewidth']     = 2
    plt.rcParams['figure.figsize']      = (12, 7)
    plt.rcParams['font.size']           = n

    plt.rcParams['axes.prop_cycle']     = plt.cycler(color=[
        'darkblue','darkviolet','deeppink','crimson','orangered','darkorange','sandybrown','gold','yellow'])
    plt.rcParams['lines.markeredgewidth'] = 2
####################################################
