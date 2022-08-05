import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import os
      
####################################################
# finding neighbor pixels
def neighborPixels(camgeom, limitDistance):
    
    X, Y = [], []
    for i in range(len(camgeom.pix_x)):
        X.append(camgeom.pix_x[i].value)
        Y.append(camgeom.pix_y[i].value)

    X = np.array(X)
    Y = np.array(Y)
    V = [[X[i], Y[i]] for i in range(len(X))]



    neigh_list = [[] for px in range(1855)]
    for px in range(1855):

        for j in range(1855):

            d = dist(V[px],V[j])
            if d < limitDistance and d != 0:

                neigh_list[px].append(j)

    PX_N  = camgeom.neighbors
    PX_NN = neigh_list    
    
    return PX_N, PX_NN
####################################################



####################################################
# finding the pixels of the selected clusters for each run
def neighborCluster(camgeom1, camgeom2, RUNS):
    
    X1, Y1 = [], []
    for i in range(len(camgeom1.pix_x)):
        X1.append(camgeom1.pix_x[i].value)
        Y1.append(camgeom1.pix_y[i].value)

    X1     = np.array(X1)
    Y1     = np.array(Y1)
    V1     = [[X1[i], Y1[i]] for i in range(len(X1))]
    X2, Y2 = [], []
    for i in range(len(camgeom2.pix_x)):
        X2.append(camgeom2.pix_x[i].value)
        Y2.append(camgeom2.pix_y[i].value)

    X2 = np.array(X2)
    Y2 = np.array(Y2)
    V2 = [[X2[i], Y2[i]] for i in range(len(X2))]

    PX1 = []
    for i in range(1855):
        for j in range(1855):
            if round(V1[i][0], 2) == round(V2[j][0], 2) and round(V1[i][1], 2) == round(V2[j][1], 2):
                PX1.append(j)   

    # transformation CaCo-LST
    CaCoCLUST = [132,114,150,96,168,79,185,63,201,48,216,34,230,21,243,9,255,131,113,149,95,167,78,184,62,200,
                 47,215,33,229,20,242,8,254,264,133,115,151,97,169,80,186,64,202,49,217,35,231,22,244,10,256,
                 0,130,112,148,94,166,77,183,61,199,46,214,32,228,19,241,253,263,134,116,152,98,170,81,187,65,
                 203,50,218,36,232,23,245,11,1,129,111,147,93,165,76,182,60,198,45,213,31,227,240,252,262,135,
                 117,153,99,171,82,188,66,204,51,219,37,233,24,12,2,128,110,146,92,164,75,181,59,197,44,212,
                 226,239,251,261,136,118,154,100,172,83,189,67,205,52,220,38,25,13,3,127,109,145,91,163,74,180,
                 58,196,211,225,238,250,260,137,119,155,101,173,84,190,68,206,53,39,26,14,4,126,108,144,90,162,
                 73,179,195,210,224,237,249,259,138,120,156,102,174,85,191,69,54,40,27,15,5,125,107,143,89,161,
                 178,194,209,223,236,248,258,139,121,157,103,175,86,70,55,41,28,16,6,124,106,142,160,177,193,
                 208,222,235,247,257,140,122,158,104,87,71,56,42,29,17,7,141,159,176,192,207,221,234,246,123,
                 105,88,72,57,43,30,18]

    def data_lst(array):
        array_tr = [0 for i in range(1855)]
        for i in range(1855):
            array_tr[i] = array[PX1[i]]

        return array_tr

    # index of pixels to check
    pixelsRun = []
    for run in range(len(RUNS)):

        clusters = [i + run * 10 for i in range(10) if i + run * 10 < 265]

        data = [0 for i in range(265)]

        for cluster in clusters:
            cluster       = CaCoCLUST.index(cluster)
            data[cluster] = 1

        data = [data[i] for i in range(265) for j in range(7)]
        data = data_lst(data)

        indexes = []
        for i in range(len(data)):
            if data[i] == 1:
                indexes.append(i)

        pixelsRun.append(indexes)
    
    return pixelsRun

####################################################



####################################################
def neighborCluster(camgeom1, camgeom2):

    X1,Y1=[],[]
    for i in range(len(camgeom1.pix_x)):
        X1.append(camgeom1.pix_x[i].value)
        Y1.append(camgeom1.pix_y[i].value)

    X1 = np.array(X1)
    Y1 = np.array(Y1)
    V1 = [[X1[i],Y1[i]] for i in range(len(X1))]
    X2,Y2=[],[]
    for i in range(len(camgeom2.pix_x)):
        X2.append(camgeom2.pix_x[i].value)
        Y2.append(camgeom2.pix_y[i].value)

    X2 = np.array(X2)
    Y2 = np.array(Y2)
    V2 = [[X2[i],Y2[i]] for i in range(len(X2))]


    PX1 = []
    for i in range(1855):
        for j in range(1855):
            if round(V1[i][0],2)==round(V2[j][0],2) and round(V1[i][1],2)==round(V2[j][1],2):
                PX1.append(j)   

    # transformation CaCo-LST
    CaCoCLUST = [132,114,150,96,168,79,185,63,201,48,216,34,230,21,243,9,255,131,113,149,95,167,78,184,62,200,
                 47,215,33,229,20,242,8,254,264,133,115,151,97,169,80,186,64,202,49,217,35,231,22,244,10,256,0,
                 130,112,148,94,166,77,183,61,199,46,214,32,228,19,241,253,263,134,116,152,98,170,81,187,65,
                 203,50,218,36,232,23,245,11,1,129,111,147,93,165,76,182,60,198,45,213,31,227,240,252,262,135,
                 117,153,99,171,82,188,66,204,51,219,37,233,24,12,2,128,110,146,92,164,75,181,59,197,44,212,
                 226,239,251,261,136,118,154,100,172,83,189,67,205,52,220,38,25,13,3,127,109,145,91,163,74,180,
                 58,196,211,225,238,250,260,137,119,155,101,173,84,190,68,206,53,39,26,14,4,126,108,144,90,162,
                 73,179,195,210,224,237,249,259,138,120,156,102,174,85,191,69,54,40,27,15,5,125,107,143,89,161,
                 178,194,209,223,236,248,258,139,121,157,103,175,86,70,55,41,28,16,6,124,106,142,160,177,193,
                 208,222,235,247,257,140,122,158,104,87,71,56,42,29,17,7,141,159,176,192,207,221,234,246,123,
                 105,88,72,57,43,30,18]

    def data_lst(array):
        array_tr = [0 for i in range(1855)]
        for i in range(1855):
            array_tr[i]=array[PX1[i]]

        return array_tr


    print('Calculating neighbors of cluster...\n')

    C_neighbor = [[] for px in range(1855)]

    for cl in range(265):

        data = [0 for i in range(265)]

        cl = CaCoCLUST.index(cl)
        data[cl] = 1

        data = [data[i] for i in range(265) for j in range(7)]
        data = data_lst(data)    

        for px in range(1855):

            if data[px]==1:

                for j in range(1855):

                    if data[j]==1 and j!=px:

                        C_neighbor[px].append(j)
    return C_neighbor
####################################################



####################################################
# defining distance over two points of the camera
def dist(v1,v2):
    return np.sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2)
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
