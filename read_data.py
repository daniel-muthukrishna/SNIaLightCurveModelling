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
                keys = keysStr.replace('(', '', 1).rsplit(')', 1)[0].split(', ')
                values = valuesStr.split()
                for i in range(len(keys)):
                    fileVars[keys[i]] = values[i]

        header = lines[11].split('|')
        columnNames = [col.strip('#').strip() for col in header]

        data = pd.read_csv(self.filename, header=None, delim_whitespace=True, skiprows=12, names=columnNames, comment='#')

        return fileVars, data

    def plot_light_curves(self, axis, cm, zorder):
        data = self.data
        label = os.path.basename(self.filename)
        if not data['Phase(T_Bmax)'].empty:
            axis.errorbar(data['Phase(T_Bmax)'], data['Abs mag'], yerr=data['Error Abs mag'], fmt=cm[1], label=label.split('_')[0], zorder=zorder, color=cm[0], alpha=0.8)

        # plt.figure()
        # plt.errorbar(data['Phase(T_Bmax)'], data['App mag'], yerr=data['Error App mag'], fmt='o')

    def bin_light_curve(self):
        phase = self.data['Phase(T_Bmax)'].values
        absMag = self.data['Abs mag'].values
        xBins = np.linspace(-20, 100, 121)
        yBinned = np.interp(x=xBins, xp=phase, fp=absMag, left=np.NaN, right=np.NaN)

        return xBins, yBinned

    def get_peaks(self, axis=None, cm=None, zorder=None):
        xBins, yBins = self.bin_light_curve()

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
            axis.plot(peakPhases, peakFluxes, 'o', color=cm[0], marker=cm[1], zorder=zorder)

        return peakPhases, peakFluxes


class PopulationStatistics(object):
    def __init__(self, filenameList, bandName):
        self.filenameList = filenameList
        self.bandName = bandName

    def plot_binned_light_curves(self, colorMarker):
        xBinsList, yBinsList, peaks, headerData = [], [], [], []
        zorder = 200

        fig, ax = plt.subplots(2, sharex=True)
        ax[0].set_title(self.bandName)
        ax[0].set_ylabel('Abs mag')
        ax[0].invert_yaxis()
        ax[1].invert_yaxis()
        ax[1].set_ylabel('Maxima')

        for i, filename in enumerate(self.filenameList):
            zorder -= 1
            lightCurve = LightCurve(filename)
            lightCurve.plot_light_curves(axis=ax[0], cm=colorMarker[i], zorder=zorder)
            try:
                xBins, yBins = lightCurve.bin_light_curve()
                peakPhases, peakFluxes = lightCurve.get_peaks(axis=ax[1], cm=colorMarker[i], zorder=zorder)
                header = lightCurve.snVars
                xBinsList.append(xBins)
                yBinsList.append(yBins)
                peaks.append([peakPhases, peakFluxes])
                headerData.append(header)
            except TypeError:
                pass

        xBinsArray, yBinsArray = np.array(xBinsList), np.array(yBinsList)
        averageLC = np.nanmean(yBinsArray, axis=0)
        errorsLC = np.nanstd(yBinsArray, axis=0)

        ax[0].plot(xBinsArray[0], averageLC, 'k-', zorder=1000)
        ax[0].fill_between(xBinsArray[0], averageLC-errorsLC, averageLC+errorsLC, alpha=0.7, zorder=1000)

        plt.xlabel('Phase (days)')
        plt.xlim(-20, 100)
        # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., ncol=1)
        plt.savefig('Figures/' + self.bandName)

        return xBinsArray, yBinsArray, np.array(peaks), headerData

    def get_mu(self, headerData):
        muList = []
        for header in headerData:
            muSnoopy = float(header['mu_Snoopy'])
            muSnoopyErr = float(header['err_mu_Snoopy'])
            muLCDM = float(header['mu_LCDM'])
            muList.append([muSnoopy, muSnoopyErr, muLCDM])

        return np.array(muList)

    def plot_mu_vs_peaks(self, muList, peaks):
        count = 0
        fig, ax = plt.subplots(2, 2, sharex='col', sharey='row')
        for (muSnoopy, muSnoopyErr, muLCDM), (peakPhases, peakFluxes) in zip(muList, peaks):
            if peakPhases.any():
                for peakPhase, peakFlux in zip(peakPhases, peakFluxes):
                    if 15 < peakPhase < 40:  # Second peak
                        ax[0, 0].errorbar(peakPhase, muSnoopy, yerr=muSnoopyErr, fmt='o', color='#1f77b4', alpha=0.5)
                        ax[0, 1].errorbar(peakFlux, muSnoopy, yerr=muSnoopyErr, fmt='o', color='#1f77b4', alpha=0.5)
                        count+=1
                    if -15 < peakPhase < 8:  # First peak
                        ax[1, 0].errorbar(peakPhase, muSnoopy, yerr=muSnoopyErr, fmt='o', color='#1f77b4', alpha=0.5)
                        ax[1, 1].errorbar(peakFlux, muSnoopy, yerr=muSnoopyErr, fmt='o', color='#1f77b4', alpha=0.5)

        ax[0, 0].set_title('Second Peak')
        ax[0, 0].set_xlabel('Phase (days)')
        ax[0, 0].set_ylabel('mu_Snoopy')

        ax[1, 0].set_title('Second Peak')
        ax[1, 0].set_xlabel('Phase (days)')
        ax[1, 0].set_ylabel('mu_Snoopy')

        ax[0, 1].set_title('First Peak')
        ax[0, 1].set_xlabel('Peak Flux')
        ax[0, 1].set_ylabel('mu_Snoopy')

        ax[1, 1].set_title('First Peak')
        ax[1, 1].set_xlabel('Peak Flux')
        ax[1, 1].set_ylabel('mu_Snoopy')

        fig.suptitle(self.bandName)
        plt.savefig("Figures/%s_mu_vs_peaks" % self.bandName)


def get_filenames(band):
    directory = os.path.join('NIR_Lowz_data', band)
    filenameList = os.listdir(directory)
    filePathList = [os.path.join(directory, f) for f in filenameList]

    return filePathList


def get_colors_and_markers():
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf', 'k', '#911eb4', '#800000', '#aa6e28']
    markers = ['o', 'v', 'P', '*', 'D', 'X', 'p', '3', 's', 'x', 'p']
    colorMarker = []
    for color in colors:
        for marker in markers:
            colorMarker.append((color, marker))
    return colorMarker


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
