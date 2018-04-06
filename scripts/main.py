import os

import matplotlib.pyplot as plt

from scripts.population_statistics import PopulationStatistics
from scripts.helpers import get_filenames, get_colors_and_markers
from scripts.optical_parameters import CompareOpticalAndNIR, common_optical_nir_sn
from scripts.plot_specific_light_curves import plot_specific_light_curves


def main():
    if not os.path.exists('Figures'):
        os.makedirs('Figures')
    bandList = ['Y', 'J']
    colorMarker = get_colors_and_markers()
    snNames = {'Y': [], 'J': [], 'H': [], 'K': []}

    # Set up figures
    fig, ax = {}, {}
    # figinfo values are (xname, yname, xlabel, ylabel, savename, sharey)
    figinfo = {0: ('', '', None, None, None, False),
               1: ('x1', 'secondMaxPhase', 'Optical Stretch, x1', '2nd max phase', '2nd_max_phase_vs_x1', True),
               2: ('secondMaxPhase', 'SecondMaxMag - FirstMaxMag',  None, '2nd - 1st max mag', None, False),
               3: ('secondMaxPhase', 'secondMaxMag', None, None, None, False),
               4: ('x1', 'secondMaxMag', None, None, None, False),
               5: ('x1', 'SecondMaxMag - FirstMaxMag', None, None, None, False),
               }
    for figname, (xname, yname, xlabel, ylabel, savename, sharey) in figinfo.items():
        fig[figname], ax[figname] = plt.subplots(len(bandList), figsize=(5, 10), sharex=True, sharey=sharey)
        if 'mag' in yname.lower() and sharey is True:
            ax[figname][0].invert_yaxis()

    # figA, axA = plt.subplots(1, figsize=(12, 10))
    # axA.invert_yaxis()
    # linestyles = ['-', '--']
    figA, axA = {}, {}
    filenameList = get_filenames('J')[0]
    for fname in filenameList:
        snName = os.path.basename(str(fname)).split('_')[0]
        figA[snName], axA[snName] = plt.subplots(1, figsize=(12, 10))
        axA[snName].invert_yaxis()
    linestyles = ['-', '--']
    for i, band in enumerate(bandList):
        filenameList, scriptDir = get_filenames(band)
        popStats = PopulationStatistics(filenameList, band)
        xBinsArray, yBinsArray, peaks, headerData = popStats.get_binned_light_curves(colorMarker=colorMarker, plot=True, bin_size=0.1, fig_spl=fig[0], ax_spl=ax[0], band_spl=band, i_spl=i, interp_kind='cubic')
        muList = popStats.get_mu(headerData)
        nirPeaks = popStats.plot_mu_vs_peaks(muList, peaks)

        opticalNIR = CompareOpticalAndNIR('data/Table_salt_snoopy_fittedParams.txt', nirPeaks, band)
        opticalNIR.nir_peaks_vs_optical_params()
        opticalNIR.plot_parameters(fig=fig[1], ax=ax[1], i=i, band=band, figinfo=figinfo[1])
        opticalNIR.plot_parameters(fig=fig[2], ax=ax[2], i=i, band=band, figinfo=figinfo[2])
        opticalNIR.plot_parameters(fig=fig[3], ax=ax[3], i=i, band=band, figinfo=figinfo[3])
        opticalNIR.plot_parameters(fig=fig[4], ax=ax[4], i=i, band=band, figinfo=figinfo[4])
        opticalNIR.plot_parameters(fig=fig[5], ax=ax[5], i=i, band=band, figinfo=figinfo[5])

        plot_specific_light_curves(filenameList='common_optical_nir', colorMarker=colorMarker, bin_size=1, band=band,
                                   nirPeaks=nirPeaks, opticalDataFilename='data/Table_salt_snoopy_fittedParams.txt',
                                   title='Light curves with x1 values', savename='lightcurves_with_x1_vals_with_offset',
                                   offsetFlag=True, plotSpline=True) #, fig_in=figA, ax_in=axA, linestyle=linestyles[i])

        plot_specific_light_curves(filenameList='common_optical_nir', colorMarker=('k', 'o'), bin_size=1, band=band,
                                   nirPeaks=nirPeaks, opticalDataFilename='data/Table_salt_snoopy_fittedParams.txt',
                                   title='', savename='', individualplots=True,
                                   offsetFlag=False, plotSpline=True, fig_in=figA, ax_in=axA, linestyle=linestyles[i])

        # lowx1List = (['sn2006kf', 'sn2006D', 'sn2006bh', 'sn2005ki'], 'low x1', 'low_x1')
        # midx1List = (['sn2007af', 'sn2007jg'], 'mid x1', 'mid_x1')
        # highx1List = (['sn2008bc', 'sn2006ax', 'sn2007le', 'sn2004ey'], 'high x1', 'high_x1')
        # for fnameList in [lowx1List, midx1List, highx1List]:
        #     plot_specific_light_curves(filenameList=fnameList[0], colorMarker=colorMarker, bin_size=1, band=band,
        #                                nirPeaks=nirPeaks, opticalDataFilename='data/Table_salt_snoopy_fittedParams.txt',
        #                                title=fnameList[1], savename=fnameList[2], offsetFlag=True, plotSpline=True)

        # Get list of sn name
        for fname in popStats.filenameList:
            snName = os.path.basename(fname).split('_')[0]
            snNames[band].append(snName)
        snNames[band] = set(snNames[band])

    #
    # common_sn = list(snNames['Y'] & snNames['J'] & snNames['H'] & snNames['K'])
    # print(common_sn)
    #
    #
    #
    # return common_sn


if __name__ == '__main__':
    main()
    # plt.show()
