import numpy  as np
import pandas as pd

from traitlets.config import Config
from ctapipe.io       import EventSource
from IPython.display  import clear_output

import auxiliar as aux

def create(run, root, folder):

    # other parameters
    dir_files = folder  # path (relative or absolute) to the .csv files that will be created

    # finding the run in the folder root
    date, subruns = aux.search(root,run)    
    
    LST_camera = aux.find_LST_num(root) # extracting the number of LST

    aux.create_folder(dir_files)        # creating the folder if dont exist
    
    # following subrun configuration
    config = Config(
        {
            'LSTEventSource': {
                'default_trigger_type': 'ucts',
                'allowed_tels': [1],
                'min_flatfield_adc': 3000,
                'min_flatfield_pixel_fraction': 0.8,
            },
        })

    # directory
    path   = root + date + '/'
    path   = path + 'LST-' + LST_camera + '.1.Run' + str(run).zfill(5) + '.' + str(0).zfill(4) + '.fits.fz'
    source = EventSource(input_url=path, config=config, max_events=10000)


    # arrays 
    mean = [[] for i in range(1855)]
    stdv = [[] for i in range(1855)]
    time =  []

    for i, ev in enumerate(source): 

        if i % 890 == 0:
            print('Run ' + str(run) + ' Subrun ' + str(0) + ' - ' + str(round(100 * i / 10000, 2)) + '%')

        for j in range(1855):
            mean[j].append('%.2f' % np.mean(ev.r0.tel[1].waveform[0][j][5:]))   # pedestal
            stdv[j].append('%.2f' % np.std( ev.r0.tel[1].waveform[0][j][5:]))   # stdv
        time.append(ev.trigger.time.value)

    print('Run ' + str(run) + ' Subrun ' + str(0) + ' - 100%')
    print('\nCreating the dataframe...')

    #we create the matrix for the dataframe
    matrix = [time]  
    names  = ['Time']
    for i in range(len(mean)):
        matrix.append(mean[i])
        matrix.append(stdv[i])
        names.append('Pixel ' + str(i + 1) + ' mean')
        names.append('Pixel ' + str(i + 1) + ' stdv')

    del mean, stdv, time

    # creating the dataframe using pandas
    data         = pd.DataFrame(np.transpose(matrix))
    data.columns = names

    del matrix, names

    # csv arxive
    data.to_csv(dir_files + 'data_Run' + str(run) + '_Subrun' + str(0) + '.csv', index=False)

    # clear memory and console
    clear_output()
    del data

    print('Finished with the pedestals file creation')