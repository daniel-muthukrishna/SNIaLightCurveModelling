import os
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from scipy import interpolate
import matplotlib.pyplot as plt


class LightCurve(object):
    def __init__(self, filename, bin_size=1):
        self.filename = filename
        self.snVars, self.data = self.get_data()
        self.bin_size = bin_size

    def get_data(self):
        """
        Retrieves the header variables and the light curve data from a supernova data file.
        
        Returns
        -------
        fileVars : dict
            File variables from the header of the input self.filename
        data : DataFrame
            The data for each epoch with data from the input self.filename
        
        """
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

        data = pd.read_csv(self.filename, header=None, delim_whitespace=True, skiprows=12, names=columnNames,
                           comment='#')

        return fileVars, data

    def plot_light_curves(self, axis, cm, zorder):
        """ Plots the light curve with error bars and a different color for each"""
        data = self.data
        label = os.path.basename(self.filename)
        if not data['Phase(T_Bmax)'].empty and axis is not None:
            axis.errorbar(data['Phase(T_Bmax)'], data['Abs mag'], yerr=data['Error Abs mag'], fmt=cm[1],
                          label=label.split('_')[0], zorder=zorder, color=cm[0], alpha=0.8)

            # plt.figure()
            # plt.errorbar(data['Phase(T_Bmax)'], data['App mag'], yerr=data['Error App mag'], fmt='o')

    def bin_light_curve(self):
        phase = self.data['Phase(T_Bmax)'].values
        absMag = self.data['Abs mag'].values
        xBins = np.arange(-10, 100, self.bin_size)
        # yBinned = np.interp(x=xBins, xp=phase, fp=absMag, left=np.NaN, right=np.NaN)
        if len(phase) <= 3:
            return None, None

        # Repeat values cause error in spline interpolation
        phase, unique_args = np.unique(phase, return_index=True)
        absMag = absMag[unique_args]

        y = interpolate.interp1d(x=phase, y=absMag, kind='slinear', bounds_error=False, fill_value=np.NaN)
        yBinned = y(xBins)
        # plt.figure()
        # plt.errorbar(phase, absMag, yerr=self.data['Error Abs mag'], fmt='o')
        # plt.plot(xBins, yBinned)
        # plt.gca().invert_yaxis()
        # plt.xlabel('Phase (days)')
        # plt.ylabel('Abs Mag')
        # plt.show()

        return xBins, yBinned

    def get_peaks(self, axis=None, cm=None, zorder=None):

        xBins, yBins = self.bin_light_curve()
        if xBins is None:
            return None, None

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
