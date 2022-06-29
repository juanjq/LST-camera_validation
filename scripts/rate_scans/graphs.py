import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import math

from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2                          import PdfFileMerger 
from scipy.stats                     import norm

# trying to import ctapipe import (needed the lstchain environament)
try:
    from ctapipe.visualization import CameraDisplay
    from ctapipe.coordinates   import EngineeringCameraFrame
    from ctapipe.instrument    import CameraGeometry
except:
    pass

import extract  as ext  # this module extract the data
import auxiliar as aux  # this module do the fitting, repair the pdfs and have the camera geometry change

# function to ensure we are in the cta environement 
def try_cta():
    camera_geom = CameraGeometry.from_name("LSTCam") # something to try if we have the environement

# multipage plot
def multiple_plot(t, data, run, ranges, m, n, clusOrPx_name, plt_limit, data_type, plot_run = True):
    
    treshold = []                                          # temporal array to save tresholds

    with PdfPages('temp/multi_graphs.pdf') as pdf:         # name of temporal pdf
        
        if plot_run == True:
            
            # defining n*m array of plots (one page)
            f, axarr = plt.subplots(m, n, sharex="col", sharey="row")
            arr_ij   = [(x, y) for x, y in np.ndindex(axarr.shape)]
            splots   = [axarr[index] for index in arr_ij]

            # we define a boolean for looking if a s-subplot is first in row or last in row
            splot_i = 0
            for s, splot in enumerate(splots):

                last_row     = m * n - s < n + 1
                first_in_row = s % n == 0
                # if we are in the last row we plot the x axis label
                if last_row:
                    splot.set_xlabel("Threshold")
                # if we are firsts in row we plot the y axis label
                if first_in_row:
                    splot.set_ylabel("Trigger rate [Hz]")

                
        # iterating through each cluster (or pixel) in the data, data[run][cluster]
        for cluster in range(len(data[run])):
            
            if data_type == 'l0' and plot_run == True :
            
                print('Pixel '+str(cluster)+'/'+str(len(data[run]))) # we print the run we are going trough to se the progress
            
            # function to eliminate the periodic noise that we find in some runs, return reduced arrays
            X , Y = ext.fix_noise(t,data[run][cluster])
            
            # PLOT
            # we plot ALL of the data (not only the filtered)
            if plot_run == True:
                splots[splot_i].plot(t, data[run][cluster], '.', markersize=0.8, label='Data', zorder = 2)
            
            #data fitting
            a , b = aux.fitting(X,Y)[:2]   # step-function fitting   a,b-> step-function parameters
            
            if (b > 0) and (b < 1000):
                treshold.append(b)         #appending the 50% treshold of the cluster to an array
            else:
                treshold.append(None)      # or none if not fitted
            
            if plot_run == True:                                               # only if we want the plots
                
                t_stepf = np.linspace(ranges[run][0], ranges[run][1], 200)     # x axis for plot the step-function
                y_stepf = aux.R(t_stepf,a,b)                                   # y axis for plot step-function
                splots[splot_i].plot(t_stepf, y_stepf, '-', lw=0.7, 
                                     alpha=0.75, zorder=1, label='Fitting')    # step funtction plot

                # 50% treshold line, only if fitting is succesfull (b > 0)
                if b > 0:
                    splots[splot_i].axvline(b,linestyle='--', color='darkorange', lw=0.5, zorder=0)
                # for the legend
                splots[splot_i].plot([], [], '--', color = 'darkorange', lw=0.5, label = 'Treshold at 50%')

                # plot configuration
                splots[splot_i].set_ylim(-plt_limit*0.05, plt_limit)           # y-limit for plotting
                
                # titles
                if b > 0:
                    splots[splot_i].set_title(clusOrPx_name + ' ' + str(cluster+1) + ', 50% Tr.=' + str(round(b, 2)))
                else:
                    splots[splot_i].set_title(clusOrPx_name + ' ' + str(cluster+1) + ', Fitting failed')

                # we plot the legend only once per page
                if splot_i == 0:
                    splots[splot_i].legend()
                #--------------------------------------------------------------

                splot_i += 1                                                   # next plot at same page            

                if splot_i == m * n:                                           # changing page
                    pdf.savefig()
                    plt.close(f)

                    # we repeat for new pages
                    f, axarr = plt.subplots(m, n, sharex="col", sharey="row")
                    arr_ij   = [(x, y) for x, y in np.ndindex(axarr.shape)]
                    splots   = [axarr[index] for index in arr_ij]
                    splot_i  = 0

                    # labeling in correspondent places
                    for s, splot in enumerate(splots):
                        last_row = (m * n) - s < n + 1
                        first_in_row = s % n == 0
                        
                        if last_row:
                            splot.set_xlabel("Threshold")
                        if first_in_row:
                            splot.set_ylabel("Trigger rate [Hz]")
                            
        if plot_run == True:
            
            pdf.savefig()    # save image
            plt.close()      # close plot
        
        return treshold
    
# plotting the histogram
def histogram_treshold_plot(tresholdRaw, mean, sigma, Nzeros, run, gain, voltage, neigh, dac, clusOrPx_name, run_failed, 
                            plot_run = True ):
    
    if (plot_run == True) or (run_failed == True):                               # if we want the plots
        
        fig, ax = plt.subplots(figsize=(7,5))

        # histogram with all the fitted data    
        yhist, xhist, patches = plt.hist(tresholdRaw, bins = 33, alpha = 0.7, color = 'royalblue', density = True)

        # gaussian fit and the mean value represented with a vertical line
        x_tresh = np.linspace(xhist[0], xhist[-1], 200)
        y_tresh = norm.pdf(x_tresh, mean, sigma)

        plt.plot(x_tresh, y_tresh,   '-', color='k',         label='Gaussian fit')
        plt.axvline(mean, linestyle='--', color='k', lw=0.8, label='Mean 50% treshold='+str(round(mean,1)))


        # parameters and save
        plt.title('Histogram: Gain = '+str(gain[run])+',  DAC '+str(dac[run])+',  Looking neighbor '
                  +str(neigh[run])+',  '+voltage[run].replace(' ','').replace('_',' ')+'\n \n '+
                 'Count of non fitted '+clusOrPx_name+'s = '+str(Nzeros)+',  Standard deviation '+
                  '$\\sigma$ = '+str(round(sigma,2)))  
        
        ax.set_xlabel('Threshold at 50%')
        ax.set_ylabel('Normalized # of ' + clusOrPx_name + 's')
        plt.legend()

        plt.savefig('temp/histogram.pdf',format='pdf')                           # save in a temporal documents folder   
        plt.close()    

# treshold plotted in function of the clusters/pixels
def cluster_treshold_plot(data, run, tresholdZero, mean, clusOrPx_name, gain, dac, voltage, neigh, run_failed, 
                          plot_run = True):
    
    if (plot_run == True) and (run_failed == False):                             # if we want the plots
        
        fig, ax = plt.subplots(figsize = (10, 5))

        # cluster/pixels index
        xtresh = np.linspace(1, len(data[run]), len(data[run]))
        
        # plot
        plt.bar(xtresh, tresholdZero, alpha = 0.6, color = 'royalblue', label = 'Treshold values')
        plt.axhline(mean, linestyle='--', lw=0.8,   color='k', label = 'Mean 50% treshold=' + str(round(mean,1)))

        # parameters and saving
        plt.title(clusOrPx_name + ' 50% treshold: Gain = ' + str(gain[run]) + ',  DAC ' + str(dac[run]) +
                  ',  Looking neighbor ' + str(neigh[run]) + ',  ' + voltage[run].replace(' ','').replace('_',' '))

        ax.set_ylabel('Threshold at 50%')
        ax.set_xlabel(clusOrPx_name + ' index')
        plt.legend()

        plt.savefig('temp/cluster_tresh.pdf', format = 'pdf')                      # save in a temporal documents folder   
        plt.close()
        

# we define a function to plot in the camera geometry
# we need to use the ctapipe environement
def cam_plot(x, mu, title, data_type, leftPlot = True):
    
    x = np.array(x)                                       # we convert the data array to numpy form
    
    if data_type == 'l1':                                 # for L1 we change the geometry to get the one of our camera
        x = x[INDEX_ORDER]

        xPixel = []
        for i in range(265):                              # for L1 we convert our pixels to clusters
            for j in range(7):
                xPixel.append(x[i])
                
    elif data_type == 'l0':                               # for L0 we dont do any geometry change (at the moment)
        xPixel = x[INDEX_ORDER_PX]
    
    camera_geom = CameraGeometry.from_name("LSTCam")      # camera geometry used from ctapipe
        
    # for the left plot
    if leftPlot == True:
        
        # gradient colormap from blue to red 
        cmap = colors.LinearSegmentedColormap.from_list("", ["#1a557e","#e7e7e7","#990000"])

        # camera plot with some parameters
        camdisplay = CameraDisplay(camera_geom.transform_to(EngineeringCameraFrame()), norm = colors.CenteredNorm(mu),
                                   title = title, image = xPixel, cmap = cmap, show_frame = False) 
        
        # colorbar
        camdisplay.add_colorbar(label = 'Treshold at 50%') 
       
    # for the right plot
    else:   
        
        # discrete colormap gray or blue
        cmap = colors.ListedColormap(['silver', '#1a557e'])
        
        # camera plot with some parameters
        camdisplay = CameraDisplay(camera_geom.transform_to(EngineeringCameraFrame()), norm = colors.CenteredNorm(0.4),
                                   title = title, image = xPixel, cmap = cmap, show_frame = False) 
    
    
# camera representations
def camera_repr(data, tresholdMean, tresholdFitting, mean, Nzeros, run, gain, dac, neigh, voltage,
                clusOrPx_name, data_type, run_failed, plot_run = True):
    
    if (plot_run == True) and (run_failed == False):                          # if we want the plots
        
        fig, ax = plt.subplots(figsize=(10, 4.5))

        # left plot---------------------
        ax1 = plt.subplot(1,2,1)

        title = (clusOrPx_name+'s 50% treshold: Gain = '+str(gain[run])+',  DAC '+str(dac[run])+
               ',  Looking neighbor '+str(neigh[run])+',  '+voltage[run].replace(' ','').replace('_',' ')+
               '\n \n (Not fitted '+clusOrPx_name+'s are represented also in gray '+
               '$\\rightarrow$ more info in right graph)')

        # we call the function to plot in the camera
        cam_plot(tresholdMean, mean, title, data_type)

        ax1.set_axis_off()
        ax1.invert_xaxis()                                                    # inverting the axis
        ax1.invert_yaxis()                                                    # because of the camera geometry

        #right plot---------------------
        ax2 = plt.subplot(1,2,2)
        if data_type == 'l1':
            
            title = ('Mean 50% treshold = '+str(round(mean,1))+' \n \n Number of '+clusOrPx_name+
                   's that we could not fit = '+str(Nzeros)+', the '+str(round((Nzeros/len(data[run])*100),1))+'%')
            
        elif data_type == 'l0':
            
            title = ('Mean 50% treshold = '+ str(round(mean,1))+' \n \n Number of '+clusOrPx_name+
                   's that we could not fit = '+str(Nzeros)+', the '+str(round((Nzeros/len(data[run])*100),1))+'%')
                    
        # we call the function to plot in the camera, but now we plot the not fitted clusters/pixels
        cam_plot(tresholdFitting,  mean, title, data_type, leftPlot = False)

        # discrete colorbar and colormap
        cmap = colors.ListedColormap(['silver', '#1a557e'])
        cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap),ticks=[ 0,0.25,0.75, 1], ax=ax2) 
        cbar.ax.set_yticklabels(['','Fitted', 'Not fitted',''])

        ax2.set_axis_off()
        ax2.invert_xaxis()                                                     # inverting the axis
        ax2.invert_yaxis()                                                     # because of the camera geometry

        plt.savefig('temp/camera_plot.pdf', format='pdf')                      # save in a temporalfolder   
        plt.close()   
        
        
# all data taken in a unique plot
def all_together_plot(data, t, run, mean, plt_limit, gain, dac, neigh, voltage, clusOrPx_name, run_failed, plot_run = True):
    
    if (plot_run == True) and (run_failed == False):                            # if we want the plots
        
        fig, ax = plt.subplots(figsize=(9,6))
        
        plt.title('All data together: Gain = '+str(gain[run])+',  DAC '+str(dac[run])+',  Looking neighbor '+
                  str(neigh[run])+',  '+voltage[run].replace(' ','').replace('_',' '))

        # the plot for each cluster
        for j in range(len(data[run]))[:265]:

            X, Y = ext.fix_noise(t.copy(), data[run][j].copy())
            plt.plot(X, Y, '.', color = 'royalblue', alpha = 0.2)

        # line with the mean treshold
        plt.axvline(mean, linestyle='--', color='k', lw=0.8, label='Mean 50% treshold='+str(round(mean,1)))

        '''#average and standard deviation calculus (uncomment to use it)
        avg,std=[],[]
        for j in range(len(data[run][0])):
            avg.append(np.mean(list(np.transpose(data[run])[j])))
            #std.append(np.std(list(np.transpose(data[run])[j])))
        plt.plot(t,avg,color='k',label='Mean value')
        #plt.fill_between(t,std,0, color='gray',alpha=0.4,label='Standard deviation')'''

        plt.ylim(-plt_limit*0.05, plt_limit)                                        # limit in y 

        plt.plot([], [], '.', color='royalblue', alpha=0.5, label='Each '+clusOrPx_name)
        plt.legend(loc = 1)

        ax.set_xlabel('Threshold')
        ax.set_ylabel('Trigger rate [Hz]')

        plt.savefig('temp/all_together.pdf', format='pdf')                          # save in a temporal folder   
        plt.close()     

#camera plot for the complete analysis
def cam_plotTOT(x, title, data_type):
    
    x = np.array(x)                                     # we convert the data array to numpy form
    
    if data_type == 'l1':                               # for L1 we change the geometry to get the one of our camera
        x = x[INDEX_ORDER]

        xPixel = []
        for i in range(265):                            # for L1 we convert our pixels to clusters
            for j in range(7):
                xPixel.append(x[i])
                
    elif data_type == 'l0':                             # for L0 we dont do any geometry change (at the moment)
        xPixel = x[INDEX_ORDER_PX]
    
    camera_geom = CameraGeometry.from_name("LSTCam")    # camera geometry used from ctapipe
        
        
    # gradient colormap from blue to red 
    cmap = colors.LinearSegmentedColormap.from_list("", ["#1a557e","#e7e7e7","#990000"])

    # camera plot with some parameters
    camdisplay = CameraDisplay(camera_geom.transform_to(EngineeringCameraFrame()), norm=colors.CenteredNorm(0),
                               title=title, image=xPixel, cmap=cmap, show_frame=False) 

    # colorbar
    camdisplay.add_colorbar(label = 'Treshold deviation') 
       
# camera total representation
def camera_reprTOT(mean_dev, data_type, clusOrPx_name):

    fig, ax = plt.subplots(figsize=(10,4.5))
    ax1     = plt.subplot(1,2,1)
    title   = ('Representation of the mean deviation of each '+clusOrPx_name)

    # we call the function to plot in the camera
    cam_plotTOT(mean_dev,title,data_type)

    ax1.set_axis_off()
    ax1.invert_xaxis()                                                           # inverting the axis
    ax1.invert_yaxis()                                                           # because of the camera geometry
    
    ax2 = plt.subplot(1,2,2)

    ax2.set_title('Most deviated pixels')
    ax2.set_axis_off()
    ax2.set_ylim(0,-7)
    ax2.set_xlim(-1,3)


    abs_dev = []
    for i in range(len(mean_dev)):
        abs_dev.append(abs(mean_dev[i]))

    index      = []
    ii         = aux.closer_element_index(abs_dev, 1000)
    index.append(ii)
    ii,abs_dev = aux.next_closer(abs_dev, 1000, ii)
    index.append(ii)
    ii,abs_dev = aux.next_closer(abs_dev, 1000, ii)
    index.append(ii)
    ii,abs_dev = aux.next_closer(abs_dev, 1000, ii)
    index.append(ii)
    ii,abs_dev = aux.next_closer(abs_dev, 1000, ii)
    index.append(ii)
    ii,abs_dev = aux.next_closer(abs_dev, 1000, ii)
    index.append(ii)

    numText=['1st', '2nd', '3rd', '4th', '5th', '6th']
    for i in [0, 1, 2, 3, 4, 5]:
        title = (numText[i] + ' deviated: '+ clusOrPx_name +' '+ str(index[i]+1)+
                 ', with deviation from mean = ' + str(round(mean_dev[index[i]],2)))

        ax2.text(-1.2, -6+i, title, fontsize=12)


    plt.savefig('temp/camera_total.pdf', format='pdf')     # save in a temporalfolder   
    plt.close()   
    
# plot the tresholds for total analysis
def tresholds_total(meanARR, sigmaARR, gain, voltage, data_type, data1run, voltageName):

    if data1run == False:                                  # if we are looking only one run, can't do a complete analysis

        neighbors = [' 0',' 1',' 2',' 3',' 4',' 5']        # possible neighbors
        gains     = [0, 7, 10, 15, 20]                     # possible gains

        # treshold mean and std vs gain (no hv)

        meanG,sigmaG = [[],[],[],[],[]],[[],[],[],[],[]]

        for run in range(len(meanARR)):
            for ga in range(len(gains)):

                    if (gain[run] == gains[ga]) and (voltage[run].replace(' ','') == voltageName ):

                        if math.isnan(meanARR[run]) == False:
                            meanG[ga].append(meanARR[run])
                            sigmaG[ga].append(sigmaARR[run])

        for i in range(len(meanG)):
            meanG[i]  = np.nanmean(meanG[i])
            sigmaG[i] = np.nanmean(sigmaG[i])


        fig, ax = plt.subplots(figsize = (9,6))

        # for the mean
        ax.set_title('Treshold at 50% for '+data_type.replace('l','L')+', for all runs with '+voltageName.replace('_',' '))
        ax.set_ylabel('Mean 50% treshold')
        ax.set_xlabel('Gain')

        plt.errorbar(gains, meanG, sigmaG, 0, capsize=3, marker='o', markerfacecolor='white', color='darkviolet')

        plt.scatter( [],[],               marker='o',       facecolor='white', label='Mean value',         color='darkviolet')
        plt.errorbar([],[],0,0,capsize=3, marker='',  markerfacecolor='white', label='Standard deviation', color='darkviolet')
        plt.legend(loc = 2)

        plt.savefig('temp/treshold_total.pdf', format='pdf')  #save in a temporal documents folder   
        plt.close()

#camera treshold deviation plot#########################################
def camera_total(treshold_devARR, data1run, plot_camera, clusOrPx_name, data_type):

    if (data1run == False) and (plot_camera == True):         #if we are looking only one run, can't do a complete analysis

        mean_dev = []
        for j in range(len(treshold_devARR[0])):

            dev_temp = []
            for run in range(len(treshold_devARR)):

                if treshold_devARR[run][j] != None:
                    dev_temp.append(treshold_devARR[run][j])

            mean_dev.append(np.mean(dev_temp))

        camera_reprTOT(mean_dev, data_type, clusOrPx_name)

# camera plot geometry indexes, converted from the geometry of the camera, to the geometry of the ctapipe github
INDEX_ORDER = [132,114,150,96,168,79,185,63,201,48,216,34,230,21,243,9,255,131,113,149,95,167,78,184,62,200,47,215,
               33,229,20,242,8,254,264,133,115,151,97,169,80,186,64,202,49,217,35,231,22,244,10,256,0,130,112,148,
               94,166,77,183,61,199,46,214,32,228,19,241,253,263,134,116,152,98,170,81,187,65,203,50,218,36,232,23,
               245,11,1,129,111,147,93,165,76,182,60,198,45,213,31,227,240,252,262,135,117,153,99,171,82,188,66,
               204,51,219,37,233,24,12,2,128,110,146,92,164,75,181,59,197,44,212,226,239,251,261,136,118,154,100,
               172,83,189,67,205,52,220,38,25,13,3,127,109,145,91,163,74,180,58,196,211,225,238,250,260,137,119,
               155,101,173,84,190,68,206,53,39,26,14,4,126,108,144,90,162,73,179,195,210,224,237,249,259,138,120,
               156,102,174,85,191,69,54,40,27,15,5,125,107,143,89,161,178,194,209,223,236,248,258,139,121,157,103,
               175,86,70,55,41,28,16,6,124,106,142,160,177,193,208,222,235,247,257,140,122,158,104,87,71,56,42,29,17,
               7,141,159,176,192,207,221,234,246,123,105,88,72,57,43,30,18]

    
INDEX_ORDER_PX = [0,3,2,1,6,5,4,33,16,17,34,56,55,32,24,44,43,23,10,11,25,119,84,85,120,160,159,118,101,139,138,100,69,70,102,259,206,207,260,318,317,258,232,288,287,231,182,183,233,453,382,383,454,530,529,452,417,491,490,416,349,350,418,701,612,613,702,796,795,700,656,748,747,655,570,571,657,1003,896,897,1004,1116,1115,1002,949,1059,1058,948,845,846,950,1359,1234,1235,1360,1490,1489,1358,1296,1424,1423,1295,1174,1175,1297,1707,1607,1608,1708,1785,1784,1706,1659,1749,1748,1658,1550,1551,1660,30,29,14,15,31,52,51,82,53,54,83,117,116,81,27,47,26,12,13,28,48,204,157,158,205,257,256,203,72,104,71,45,46,73,105,380,315,316,381,451,450,379,141,185,184,140,103,142,186,610,527,528,611,699,698,609,290,352,351,289,234,235,291,894,793,794,895,1001,1000,893,493,573,572,492,419,420,494,1232,1113,1114,1233,1357,1356,1231,750,848,847,749,658,659,751,1605,1487,1488,1606,1705,1704,1604,1061,1177,1176,1060,951,952,1062,1832,1782,1783,1833,1852,1851,1831,1426,1553,1552,1425,1298,1299,1427,1751,1814,1813,1750,1661,1662,1752,21,22,40,39,20,8,9,36,7,19,60,59,35,18,67,99,98,66,41,42,68,87,58,88,123,122,86,57,180,230,229,179,136,137,181,162,121,163,210,209,208,161,347,415,414,346,285,286,348,320,261,262,321,385,384,319,568,654,653,567,488,489,569,532,455,456,533,615,614,531,843,947,946,842,745,746,844,798,703,704,799,899,898,797,1172,1294,1293,1171,1056,1057,1173,1118,1005,1006,1119,1237,1236,1117,1548,1657,1656,1547,1421,1422,1549,1492,1361,1362,1493,1610,1609,1491,1811,1846,1845,1810,1746,1747,1812,1787,1709,1710,1788,1835,1834,1786,113,112,79,80,114,153,152,155,154,115,156,202,201,200,77,76,49,50,78,111,110,313,254,255,314,378,377,312,107,145,106,74,75,108,146,525,448,449,526,608,607,524,188,238,187,143,144,189,239,791,696,697,792,892,891,790,293,355,292,236,237,294,356,1111,998,999,1112,1230,1229,1110,422,496,421,353,354,423,497,1485,1354,1355,1486,1603,1602,1484,575,661,660,574,495,576,662,1780,1702,1703,1781,1830,1829,1779,850,954,953,849,752,753,851,1179,1301,1300,1178,1063,1064,1180,1555,1664,1663,1554,1428,1429,1556,95,96,132,131,94,64,65,62,63,93,92,61,37,38,134,178,177,176,133,97,135,125,90,126,167,166,124,89,283,345,344,282,227,228,284,212,165,213,266,265,211,164,486,566,565,485,412,413,487,323,264,324,389,388,322,263,743,841,840,742,651,652,744,458,387,459,536,535,457,386,1054,1170,1169,1053,944,945,1055,617,534,618,707,706,705,616,1419,1546,1545,1418,1291,1292,1420,901,800,801,902,1008,1007,900,1744,1809,1808,1743,1654,1655,1745,1239,1120,1121,1240,1364,1363,1238,1612,1494,1495,1613,1712,1711,1611,250,249,198,199,251,308,307,310,309,252,253,311,374,373,196,195,150,151,197,248,247,446,375,376,447,523,522,445,148,192,147,109,149,194,193,694,605,606,695,789,788,693,241,297,240,190,191,242,298,996,889,890,997,1109,1108,995,358,426,357,295,296,359,427,1352,1227,1228,1353,1483,1482,1351,499,579,498,424,425,500,580,1700,1600,1601,1701,1778,1777,1699,664,756,663,577,578,665,757,853,957,852,754,755,854,958,1066,1182,1065,955,956,1067,1183,1303,1431,1430,1302,1181,1304,1432,223,224,278,277,222,174,175,172,173,221,220,171,129,130,280,281,341,340,279,225,226,127,128,170,169,216,168,91,410,484,483,409,342,343,411,268,215,269,328,327,267,214,649,741,740,648,563,564,650,391,326,392,463,462,390,325,942,1052,1051,941,838,839,943,538,461,539,622,621,537,460,1289,1417,1416,1288,1167,1168,1290,709,620,710,805,804,708,619,1652,1742,1741,1651,1543,1544,1653,904,803,905,1012,1011,903,802,1123,1010,1124,1243,1242,1122,1009,1366,1241,1367,1498,1497,1496,1365,441,440,371,372,442,517,516,519,518,443,444,520,601,600,369,368,305,306,370,439,438,603,602,521,604,692,691,690,303,302,245,246,304,367,366,887,786,787,888,994,993,886,300,362,299,243,244,301,363,1225,1106,1107,1226,1350,1349,1224,429,503,428,360,361,430,504,1598,1480,1481,1599,1698,1697,1597,582,668,581,501,502,583,669,759,857,758,666,667,760,858,960,1070,959,855,856,961,1071,1185,1307,1184,1068,1069,1186,1308,1434,1557,1433,1305,1306,1435,1558,405,406,478,477,404,338,339,336,337,403,402,335,275,276,480,481,559,558,479,407,408,273,274,334,333,272,218,219,561,647,646,645,560,482,562,330,217,271,396,395,329,270,836,940,939,835,738,739,837,465,394,466,543,542,464,393,1165,1287,1286,1164,1049,1050,1166,624,541,625,714,713,623,540,1541,1650,1649,1540,1414,1415,1542,807,712,808,909,908,806,711,1014,907,1015,1128,1127,1013,906,1245,1126,1246,1371,1370,1244,1125,1500,1369,1501,1615,1614,1499,1368,686,685,598,599,687,780,779,782,781,688,689,783,882,881,596,595,514,515,597,684,683,884,883,784,785,885,990,989,512,511,436,437,513,594,593,1104,991,992,1105,1223,1222,1103,434,433,364,365,435,510,509,1478,1347,1348,1479,1596,1595,1477,506,586,505,431,432,507,587,671,763,670,584,585,672,764,860,964,859,761,762,861,965,1073,1189,1072,962,963,1074,1190,1310,1438,1309,1187,1188,1311,1439,1560,1665,1559,1436,1437,1561,1666,641,642,732,731,640,556,557,554,555,639,638,553,475,476,734,735,831,830,733,643,644,473,474,552,551,472,400,401,833,834,936,935,832,736,737,398,399,471,470,397,331,332,1047,1163,1162,1046,937,938,1048,545,468,546,629,628,544,467,1412,1539,1538,1411,1284,1285,1413,716,627,717,812,811,715,626,911,810,912,1019,1018,910,809,1130,1017,1131,1250,1249,1129,1016,1373,1248,1374,1505,1504,1372,1247,1617,1503,1618,1714,1713,1616,1502,985,984,879,880,986,1097,1096,1099,1098,987,988,1100,1217,1216,877,876,777,778,878,983,982,1219,1218,1101,1102,1220,1343,1342,775,774,681,682,776,875,874,1345,1344,1221,1346,1476,1475,1474,679,678,591,592,680,773,772,589,675,588,508,590,677,676,766,864,765,673,674,767,865,967,1077,966,862,863,968,1078,1192,1314,1191,1075,1076,1193,1315,1441,1564,1440,1312,1313,1442,1565,1668,1753,1667,1562,1563,1669,1754,931,932,1040,1039,930,828,829,826,827,929,928,825,729,730,1042,1043,1157,1156,1041,933,934,727,728,824,823,726,636,637,1159,1160,1280,1279,1158,1044,1045,634,635,725,724,633,549,550,1282,1410,1409,1408,1281,1161,1283,547,548,632,631,720,630,469,814,719,815,916,915,813,718,1021,914,1022,1135,1134,1020,913,1252,1133,1253,1378,1377,1251,1132,1507,1376,1508,1622,1621,1506,1375,1716,1620,1717,1790,1789,1715,1619,1338,1337,1214,1215,1339,1468,1467,1470,1469,1340,1341,1471,1591,1590,1212,1211,1094,1095,1213,1336,1335,1593,1592,1472,1473,1594,1696,1695,1092,1091,980,981,1093,1210,1209,978,977,872,873,979,1090,1089,870,869,770,771,871,976,975,867,971,866,768,769,868,972,1080,1196,1079,969,970,1081,1197,1317,1445,1316,1194,1195,1318,1446,1567,1672,1566,1443,1444,1568,1673,1756,1815,1755,1670,1671,1757,1816,1275,1276,1402,1401,1274,1154,1155,1152,1153,1273,1272,1151,1037,1038,1404,1405,1534,1533,1403,1277,1278,1035,1036,1150,1149,1034,926,927,1536,1537,1648,1647,1535,1406,1407,924,925,1033,1032,923,821,822,819,820,922,921,818,722,723,918,721,817,1026,1025,917,816,1137,1024,1138,1257,1256,1136,1023,1380,1255,1381,1512,1511,1379,1254,1624,1510,1625,1721,1720,1623,1509,1792,1719,1793,1837,1836,1791,1718,1691,1690,1588,1589,1692,1773,1772,1775,1774,1693,1694,1776,1828,1827,1586,1585,1465,1466,1587,1689,1688,1463,1462,1333,1334,1464,1584,1583,1331,1330,1207,1208,1332,1461,1460,1205,1204,1087,1088,1206,1329,1328,1085,1084,973,974,1086,1203,1202,1199,1321,1198,1082,1083,1200,1322,1448,1571,1447,1319,1320,1449,1572,1675,1760,1674,1569,1570,1676,1761,1818,1847,1817,1758,1759,1819,1848,1643,1644,1737,1736,1642,1531,1532,1529,1530,1641,1640,1528,1399,1400,1739,1740,1807,1806,1738,1645,1646,1397,1398,1527,1526,1396,1270,1271,1268,1269,1395,1394,1267,1147,1148,1145,1146,1266,1265,1144,1030,1031,1028,1029,1143,1142,1027,919,920,1259,1140,1260,1385,1384,1258,1139,1514,1383,1515,1629,1628,1513,1382,1723,1627,1724,1797,1796,1722,1626,1839,1795,1840,1854,1853,1838,1794,1825,1824,1770,1771,1826,1850,1849,1768,1767,1686,1687,1769,1823,1822,1684,1683,1581,1582,1685,1766,1765,1579,1578,1458,1459,1580,1682,1681,1456,1455,1326,1327,1457,1577,1576,1324,1452,1323,1201,1325,1454,1453,1574,1679,1573,1450,1451,1575,1680,1763,1820,1762,1677,1678,1764,1821,1804,1805,1844,1843,1803,1734,1735,1732,1733,1802,1801,1731,1638,1639,1636,1637,1730,1729,1635,1524,1525,1522,1523,1634,1633,1521,1392,1393,1390,1391,1520,1519,1389,1263,1264,1261,1262,1388,1387,1518,1386,1141,1631,1517,1632,1728,1727,1630,1516,1799,1726,1800,1842,1841,1798,1725]