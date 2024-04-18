import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import os
      
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
# function to perform one event plot
def event_waveforms_plot(event_index, waveforms):
    
    event_index = event_index-1
    
    parameters()
    fig,ax = plt.subplots(figsize=(7,4)) 
    
    for px in range(len(waveforms[event_index])):
        
        # random blue color
        color = (np.random.choice(np.linspace(0.2,0.5,10)),np.random.choice(np.linspace(0,1,10)),
                 np.random.choice([0.7,0.8,0.9,1]))
        # plot the waveforms
        ax.plot(waveforms[event_index][px], color=color, alpha=0.5, lw=1.5)

    ax.set_xlabel('t (ns)')
    ax.set_ylabel('charge')
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
