import os

import matplotlib.pyplot as plt

from scripts.population_statistics import PopulationStatistics
from scripts.helpers import get_filenames, get_colors_and_markers
from scripts.optical_parameters import CompareOpticalAndNIR


def main():
    if not os.path.exists('Figures'):
        os.makedirs('Figures')
    bandList = ['Y', 'J', 'H', 'K']
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

    for i, band in enumerate(bandList):
        filenameList, scriptDir = get_filenames(band)
        popStats = PopulationStatistics(filenameList, band)
        xBinsArray, yBinsArray, peaks, headerData = popStats.get_binned_light_curves(colorMarker=colorMarker, plot=True, bin_size=1, fig_spl=fig[0], ax_spl=ax[0], band_spl=band, i_spl=i)
        muList = popStats.get_mu(headerData)
        labelledMaxima = popStats.plot_mu_vs_peaks(muList, peaks)

        opticalNIR = CompareOpticalAndNIR('data/Table_salt_snoopy_fittedParams.txt', labelledMaxima, band)
        opticalNIR.nir_peaks_vs_optical_params()
        opticalNIR.plot_parameters(fig=fig[1], ax=ax[1], i=i, band=band, figinfo=figinfo[1])
        opticalNIR.plot_parameters(fig=fig[2], ax=ax[2], i=i, band=band, figinfo=figinfo[2])
        opticalNIR.plot_parameters(fig=fig[3], ax=ax[3], i=i, band=band, figinfo=figinfo[3])
        opticalNIR.plot_parameters(fig=fig[4], ax=ax[4], i=i, band=band, figinfo=figinfo[4])
        opticalNIR.plot_parameters(fig=fig[5], ax=ax[5], i=i, band=band, figinfo=figinfo[5])


        # Get list of sn name
        for fname in popStats.filenameList:
            snName = os.path.basename(fname).split('_')[0]
            snNames[band].append(snName)
        snNames[band] = set(snNames[band])

    common_sn = list(snNames['Y'] & snNames['J'] & snNames['H'] & snNames['K'])
    print(common_sn)
    return common_sn


if __name__ == '__main__':
    main()
    plt.show()
