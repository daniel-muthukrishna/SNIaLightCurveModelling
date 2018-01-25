import os
import matplotlib.pyplot as plt
from population_statistics import PopulationStatistics, get_filenames, get_colors_and_markers


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
        popStats.plot_mu_vs_peaks(muList, peaks)

    plt.show()


if __name__ == '__main__':
    main()
