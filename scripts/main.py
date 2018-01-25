import os

import matplotlib.pyplot as plt

from scripts.population_statistics import PopulationStatistics
from scripts.helpers import get_filenames, get_colors_and_markers
from scripts.optical_parameters import CompareOpticalAndNIR


def main():
    if not os.path.exists('Figures'):
        os.makedirs('Figures')
    bandList = ['H_band', 'J_Band', 'K_band', 'Y_Band']
    colorMarker = get_colors_and_markers()

    for band in bandList:
        filenameList = get_filenames(band)
        popStats = PopulationStatistics(filenameList, band)
        xBinsArray, yBinsArray, peaks, headerData = popStats.plot_binned_light_curves(colorMarker)
        muList = popStats.get_mu(headerData)
        labelledMaxima = popStats.plot_mu_vs_peaks(muList, peaks)

        opticalNIR = CompareOpticalAndNIR('data/Table_salt_snoopy_fittedParams.txt', labelledMaxima, band)
        opticalNIR.nir_peaks_vs_optical_params()

    plt.show()


if __name__ == '__main__':
    main()
