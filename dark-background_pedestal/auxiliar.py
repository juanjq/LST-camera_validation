import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
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
# function to read the csv files in the Pedestal files
def readPedestal(path):
    print('Reading CSV...')
    df  = pd.read_csv(path)

    pedestal = []
    stdv     = []
    time     = df.iloc[:,0]
    time     = time - time[0]     #taking as reference the 0 time

    for i in range(1855): 

        pedestal.append(df.iloc[:,i*2+1])
        stdv.append(df.iloc[:,i*2+2])

    del df  # cleaning memory    
    
    return pedestal, stdv, time
####################################################



####################################################
# function to read the csv files in the ns scale analysis
def readNS(path):
    
    print('Reading CSV...')
    df  = pd.read_csv(path)

    random_pixels = len(df.columns)-1

    charges  = []
    time     = np.array(df.iloc[1:,0])
    time     = time - time[0]          # taking as reference the 0 time
    pixels   = np.array(df.iloc[0][1:])
    pixels   = [int(pixels[i]) for i in range(len(pixels))]

    for px in range(random_pixels): 

        temp = []
        for ev in range(len(time)):
            ch = np.array(df.iloc[ev+1][px+1][1:-1].replace(' ','').split(','))
            temp.append([int(ch[i]) for i in range(len(ch))])

        charges.append(temp)

    del df  # cleaning memory
    
    return charges, time, pixels, random_pixels
####################################################



####################################################
# function that automatically filters the frequencies and finds the lower high amplitude frequency
def freqFilterPedestal(f, fftPedestal):   
    
    # ---------- searching for the limit in amplitud ---------- #
    repetitions  = 15
    rand_indexes = [int(np.random.random() * 1855) for i in range(repetitions)]

    max3Array = []
    for rand_index in rand_indexes:

        # maximums for 2nd graphic
        max2list=list(abs(fftPedestal[rand_index]).copy())
        max2list.sort()
        max2=max2list[-2]
        min2= min(abs(fftPedestal[rand_index]))

        # maximums for 3rd graphic
        max3list=list(abs(fftPedestal[rand_index]).copy())
        max3list.sort()
        max3=max2list[-30]
        min3= min(abs(fftPedestal[rand_index]))

        max3Array.append(max3)

    # limit we impose in the frequency filtering
    AMPL_LIM = (7 * max(max3Array) + np.mean(max3Array)) / 8

    print('The limit in the frequency filtering is ' + str(round(AMPL_LIM,2)) + '\n')
  

    # ------ filtering ------ #
    # frequencies filtered
    freq_px   = []
    ampl_px   = []
    freqTotal = []
    print('Start filtering...')
    for px in range(len(fftPedestal)):
        tempF = []
        tempA = []

        if px % 200 == 0 :
            print('Filtering... ' + str(round(100 * px / 1855, 2)) + '%')

        for ev in range(len(fftPedestal[px])):
            if (abs(fftPedestal[px][ev]) > AMPL_LIM):
                tempF.append(f[ev])
                tempA.append(fftPedestal[px][ev])
                freqTotal.append(f[ev])

        freq_px.append(tempF)
        ampl_px.append(tempA)

    print('Filtering    100%\n')

    # ------ finding minimum freq with high amplitude ------ #
    # repeating the frequency finding for different pixels
    f_min = []
    for rep in range(20):

        rand_index  = int(np.random.random() * 1855)
        freq_sample = freq_px[rand_index][int(len(freq_px[rand_index]) / 2):]
        ampl_sample = ampl_px[rand_index][int(len(ampl_px[rand_index]) / 2):]
        max_freq    = max(f)

        for i in range(len(freq_sample)):
            freq_diff_0 = abs(freq_sample[i]) > max_freq * 0.01
            high_ampl   = abs(ampl_sample[i]) > 0.0005 * abs(max(ampl_sample))

            if freq_diff_0 and high_ampl:

                f_min.append(round(freq_sample[i],5))
                break

    # most common function finder
    def most_common(array):
        return max(set(array), key=array.count)

    MIN_FREQ = most_common(f_min)

    print('The smallest multiple frequency is ' + str(round(MIN_FREQ, 5)) + '\n')
    
    
    
    # ---------- plotting the limits ---------- #
    print('fft of Pixel ' + str(rand_indexes[-1])+' and the respective points found\n')    

    fig, (ax1,ax2,ax3) = plt.subplots(1,3,figsize=(19,6))
    fig.tight_layout(pad=2.3)

    ax1.plot(f, abs(fftPedestal[rand_indexes[-1]]), color='crimson')
    ax1.set_yscale('log')
    ax1.set_ylabel('Amplitude')
    ax1.set_xlabel('frequency (Hz)')

    ax2.plot(f, abs(fftPedestal[rand_indexes[-1]]), color='crimson')
    ax2.set_ylim( - (max2 - min2) * 0.03, max2 + (max2 - min2) * 0.1)
    ax2.axvline(MIN_FREQ, color='b', linestyle='-', linewidth=16, alpha=0.2,
                label='Minimum h.a. \n frequency')
    ax2.set_xlabel('frequency (Hz)')             

    ax3.plot(f, abs(fftPedestal[rand_indexes[-1]]), color='crimson')
    ax3.set_ylim( - (max3 - min3) * 0.03, AMPL_LIM + (AMPL_LIM - min3) * 0.1)
    ax3.set_xlabel('frequency (Hz)') 

    ax3.axhline(AMPL_LIM, color='k', linewidth=4, label='Auto-selected limit')

    ax3.legend(loc=10)
    ax2.legend(loc=2)
    plt.show()
    
    
    
    # finding the minimum multiple frequency with higher amplitudes 
    abs_f    = abs(np.array(freqTotal))
    f_around = [abs_f[i] for i in range(len(abs_f)) if abs(abs_f[i] - MIN_FREQ) < MIN_FREQ * 0.1]

    print('\nThe high amplitudes are multiples of: '+str(round(np.mean(f_around),3))+' Hz \n\n\n')
    
    return abs_f, f_around
####################################################



####################################################
def freqFilterNS(f, fftCharge, pixels): 

    # searching for the limit in amplitud
    rand_indexes = [i for i in range(len(pixels))]

    max3Array = []
    for rand_index in rand_indexes:

        # maximums for 2nd graphic
        max2list=list(abs(fftCharge[rand_index]).copy())
        max2list.sort()
        max2=max2list[-2]
        min2= min(abs(fftCharge[rand_index]))

        # maximums for 3rd graphic
        max3list=list(abs(fftCharge[rand_index]).copy())
        max3list.sort()
        max3=max2list[-30]
        min3= min(abs(fftCharge[rand_index]))

        max3Array.append(max3)

    # limit we impose in the frequency filtering
    AMPL_LIM = (7 * max(max3Array) + np.mean(max3Array)) / 8

    print('The limit in the frequency filtering is ' + str(round(AMPL_LIM,2)) + '\n')

    # full set of frequencies filtered
    freq_px   = []
    ampl_px   = []
    freqTotal = []

    print('Start filtering...')
    for px in range(len(fftCharge)):
        tempF = []
        tempA = []

        if px % 200 == 0 :
            print('Filtering... ' + str(round(100 * px / 1855, 2)) + '%')

        for ev in range(len(fftCharge[px])):
            if (abs(fftCharge[px][ev]) > AMPL_LIM):
                tempF.append(f[ev])
                tempA.append(fftCharge[px][ev])
                freqTotal.append(f[ev])

        freq_px.append(tempF)
        ampl_px.append(tempA)


    print('Filtering    100%\n')

    # repeating the frequency finding for different pixels
    f_min = []
    for rep in range(len(rand_indexes)):

        rand_index  = rand_indexes[rep]
        freq_sample = freq_px[rand_index][int(len(freq_px[rand_index]) / 2):]
        ampl_sample = ampl_px[rand_index][int(len(ampl_px[rand_index]) / 2):]
        max_freq    = max(f)

        for i in range(len(freq_sample)):
            freq_diff_0 = abs(freq_sample[i]) > max_freq * 0.01
            high_ampl   = abs(ampl_sample[i]) > 0.0005 * abs(max(ampl_sample))

            if freq_diff_0 and high_ampl:

                f_min.append(round(freq_sample[i],5))
                break

    # most common function finder
    def most_common(array):
        return max(set(array), key=array.count)

    MIN_FREQ = most_common(f_min)

    print('The smallest multiple frequency is ' + str(round(MIN_FREQ,5)) + '\n')

    # finding the minimum multiple frequency with higher amplitudes 
    abs_f    = abs(np.array(freqTotal))
    f_around = [abs_f[i] for i in range(len(abs_f)) if abs(abs_f[i] - MIN_FREQ) < MIN_FREQ * 0.1]

    print('\nThe high amplitudes are multiples of: '+str(round(np.mean(f_around),3))+' Hz \n\n\n')

    return abs_f, f_around
####################################################



####################################################
# plot of the fourier transforms of the pedestals and stdv's
def plot_fftsPedestal(random_pixels, RUN, subrun, time, pedestal, stdv, fftPedestal, fftStdv, meanPedestal, meanStdv,
                      graphs_format, dir_graphs, f):
    
    # selecting random pixels
    indexes = np.random.rand(random_pixels) * 1855
    indexes = [int(indexes[i]) for i in range(len(indexes))]

    for index in indexes:
        print('Pixel ' + str(index+1) + ': ')

        fig,(ax1,ax2) = plt.subplots(2,1, figsize=(14,8))

        # mean
        ax1.plot(time, pedestal[index], '-', color='darkblue')
        ax1.plot([0, time[time.size-1] - time[0]], [meanPedestal[index], meanPedestal[index]], '--',
                 color='darkorange', label='Pedestal mean = ' + str(round(meanPedestal[index], 1)))

        ax1.set_title('Pixel ' + str(index+1))
        ax1.legend(loc=1)
        ax1.set_ylabel('Pedestal')
        ax1.set_xlabel('t (s)')

        # mean fft
        ax2.plot(f, abs(fftPedestal[index]), '-', color='royalblue')

        ax2.set_yscale('log')
        ax2.set_ylabel('fft(pedestal)')
        ax2.set_xlabel('f (Hz)')

        fig.tight_layout()
        plt.savefig(dir_graphs + 'fft_pedestal_Run' + str(RUN) + '_Subrun' + str(subrun) + '_px' +
                    str(index) + '.' + graphs_format, bbox_inches='tight', format=graphs_format)
        plt.show()

        fig,(ax1,ax2) = plt.subplots(2,1, figsize=(14,8))

        # stdv
        ax1.plot(time, stdv[index], '-', color='crimson')
        ax1.plot([0, time[time.size-1] - time[0]], [meanStdv[index], meanStdv[index]], '--', color='k',
                 label='STDV mean = ' + str(round(meanStdv[index], 1)))

        ax1.set_title('Pixel ' + str(index+1))
        ax1.legend(loc=1)
        ax1.set_ylabel('Standard Deviation')
        ax1.set_xlabel('t (s)')

        # stdv fft
        ax2.plot(f, abs(fftStdv[index]), '-', color='deeppink')

        ax2.set_yscale('log')
        ax2.set_ylabel('fft(STDV)')
        ax2.set_xlabel('f (Hz)')

        fig.tight_layout()
        plt.savefig(dir_graphs + 'fft_stdv_Run' + str(RUN) + '_Subrun' + str(subrun) + '_px' +
                    str(index) + '.' + graphs_format, bbox_inches='tight', format=graphs_format)
        plt.show()  
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