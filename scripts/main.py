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
    fig_x1, ax_x1 = plt.subplots(len(bandList), figsize=(6, 10), sharex=True, sharey=True)
    fig_secondmax, ax_secondmax = plt.subplots(len(bandList), figsize=(6, 10), sharex=True)
    fig_spline, ax_spline = plt.subplots(len(bandList), figsize=(6, 10), sharex=True)

    for i, band in enumerate(bandList):
        filenameList, scriptDir = get_filenames(band)
        popStats = PopulationStatistics(filenameList, band)
        xBinsArray, yBinsArray, peaks, headerData = popStats.get_binned_light_curves(colorMarker=colorMarker, plot=True, bin_size=1, fig_spl=fig_spline, ax_spl=ax_spline, band_spl=band, i_spl=i)
        muList = popStats.get_mu(headerData)
        labelledMaxima = popStats.plot_mu_vs_peaks(muList, peaks)

        opticalNIR = CompareOpticalAndNIR('data/Table_salt_snoopy_fittedParams.txt', labelledMaxima, band)
        opticalNIR.nir_peaks_vs_optical_params()
        # opticalNIR.x1_vs_second_max_phase()
        opticalNIR.plot_parameters(fig=fig_x1, ax=ax_x1, i=i, band=band, xname='secondMaxPhase', yname='x1', xlabel='2nd max phase', ylabel='Optical Stretch, x1', savename='2nd_max_phase_vs_x1')
        opticalNIR.plot_parameters(fig=fig_secondmax, ax=ax_secondmax, i=i, band=band, xname='secondMaxPhase', yname='SecondMaxMag - FirstMaxMag', ylabel='2nd - 1st max mag')

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
