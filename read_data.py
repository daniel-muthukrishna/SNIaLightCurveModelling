import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


class LightCurve(object):
    def __init__(self, filename):
        self.filename = filename
        self.snVars, self.data = self.get_data()

    def get_data(self):
        with open(self.filename, 'r') as FileObj:
            lines = FileObj.readlines()

        snName = lines[0].split()[1]
        fileVars = {'snName': snName}
        for line in lines[:10]:
            if line[0] != '#':
                valuesStr, keysStr = line.split(' # ')
                keys = keysStr.replace('(', '', 1).rsplit(')', 1)[0].split(',')
                values = valuesStr.split()
                for i in range(len(keys)):
                    fileVars[keys[i]] = values[i]

        header = lines[11].split('|')
        columnNames = [col.strip('#').strip() for col in header]

        data = pd.read_csv(self.filename, header=None, delim_whitespace=True, skiprows=12, names=columnNames, comment='#')

        return fileVars, data

    def plot_light_curves(self, axis, cm):
        data = self.data
        label = os.path.basename(self.filename)
        if not data['Phase(T_Bmax)'].empty:
            axis.errorbar(data['Phase(T_Bmax)'], data['Abs mag'], yerr=data['Error Abs mag'], fmt=cm[1], label=label.split('_')[0], zorder=1, color=cm[0])


        # plt.figure()
        # plt.errorbar(data['Phase(T_Bmax)'], data['App mag'], yerr=data['Error App mag'], fmt='o')

    def bin_light_curve(self):
        phase = self.data['Phase(T_Bmax)'].values
        absMag = self.data['Abs mag'].values
        xBins = np.linspace(-20, 100, 121)
        yBinned = np.interp(x=xBins, xp=phase, fp=absMag, left=np.NaN, right=np.NaN)

        return xBins, yBinned

    def get_peaks(self, axis=None, cm=None):
        xBins, yBins = self.bin_light_curve()
        t=0

        peakIndexes = argrelextrema(yBins, np.less)
        peakPhases = xBins[peakIndexes]
        peakFluxes = yBins[peakIndexes]

        troughIndexes = argrelextrema(yBins, np.greater)
        troughPhases = xBins[troughIndexes]
        deleteIndexes = []
        peakSep = 4  # peak must be at least 'peakSep' days from a minimum assuming binning is in days

        for j, trough in enumerate(troughPhases):
            countTroughsNearPeak = 0
            for i, peak in enumerate(xBins[peakIndexes]):
                if (peak - peakSep) < trough < (peak + peakSep):
                    countTroughsNearPeak += 1
                    if countTroughsNearPeak == 1:
                        deleteIndexes.append(i)
                    break
        peakPhases = np.delete(peakPhases, deleteIndexes)
        peakFluxes = np.delete(peakFluxes, deleteIndexes)

        if axis is not None:
            axis.plot(peakPhases, peakFluxes, 'o', color=cm[0], marker=cm[1])

        return peakPhases, peakFluxes


def get_filenames(band):
    directory = os.path.join('NIR_Lowz_data', band)
    filenameList = os.listdir(directory)
    filePathList = [os.path.join(directory, f) for f in filenameList]

    return filePathList


def main():
    bandList = ['H_band', 'J_Band', 'K_band', 'Y_Band']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf', 'k', '#911eb4', '#800000', '#aa6e28']
    markers = ['o', 'v', 'P', '*', 'D', 'X', 'p', '3', 's', 'x', 'p']
    colorMarker = []
    for color in colors:
        for marker in markers:
            colorMarker.append((color, marker))

    for band in bandList:
        xBinsList, yBinsList = [], []
        fig, ax = plt.subplots(2, sharex=True)
        ax[0].set_title(band)
        ax[0].set_ylabel('Abs mag')
        ax[0].invert_yaxis()
        ax[1].invert_yaxis()
        ax[1].set_ylabel('Maxima')

        filenameList = get_filenames(band)
        for i, filename in enumerate(filenameList):
            lightCurve = LightCurve(filename)
            lightCurve.plot_light_curves(axis=ax[0], cm=colorMarker[i])
            try:
                xBins, yBins = lightCurve.bin_light_curve()
                xBinsList.append(xBins)
                yBinsList.append(yBins)
                peakPhases, peakFluxes = lightCurve.get_peaks(axis=ax[1], cm=colorMarker[i])
            except TypeError:
                pass
        xBinsArray, yBinsArray = np.array(xBinsList), np.array(yBinsList)
        averageLC = np.nanmean(yBinsArray, axis=0)
        errorsLC = np.nanstd(yBinsArray, axis=0)

        ax[0].plot(xBinsArray[0], averageLC, 'k-', zorder=10)
        ax[0].fill_between(xBinsArray[0], averageLC-errorsLC, averageLC+errorsLC, alpha=0.7, zorder=10)


        plt.xlabel('Phase (days)')
        plt.xlim(-20, 100)
        plt.savefig(band)

        # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., ncol=1)
    plt.show()


if __name__ == '__main__':
    main()
