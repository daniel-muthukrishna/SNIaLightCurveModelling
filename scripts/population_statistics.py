import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .fit_light_curve import LightCurve


class PopulationStatistics(object):
    def __init__(self, filenameList, bandName):
        self.filenameList = filenameList
        self.bandName = bandName

    def get_binned_light_curves(self, colorMarker=None, plot=True, bin_size=1):
        """ Get the peaks and header data for each supernova. And plot the binned light curves.
        
        Parameters
        ----------
        colorMarker : tuple
            First index is the color, the second index is the marker type. E.g. ('blue', '.')
            If set to None then ensure that plot=False.

        plot : boolean
            Set True to plot light curves. If True, colorMarker must not be None
        
        Returns
        -------
        xBinsArray : 1D numpy array
            Binned values of the supernova age.
        yBinsArray : 1D numpy array
            Binned values of the supernova flux.
        peaks : pandas DataFrame
            Each row in the DataFrame contains information about each supernova, respectively. 
            Each column is a 2 x 1 list of the phase and flux of a peak/maximum of the light curve.
        headerData : pandas DataFrame
            Each row in the DataFrame contains information about each supernova, respectively.
            The columns contain the values from the header of each supernova data file (from self.filename). 
        """

        xBinsList, yBinsList, peaks, headerData = [], [], {}, {}
        zorder = 200

        if plot is True:
            fig, ax = plt.subplots(2, sharex=True)
            ax[0].set_title(self.bandName)
            ax[0].set_ylabel('Abs mag')
            ax[0].invert_yaxis()
            ax[1].invert_yaxis()
            ax[1].set_ylabel('Maxima')
        else:
            ax = None, None
            colorMarker = [None]*len(self.filenameList)

        for i, filename in enumerate(self.filenameList):
            snName = os.path.basename(filename).split('_')[0]
            zorder -= 1
            lightCurve = LightCurve(filename, bin_size=bin_size)
            if plot:
                lightCurve.plot_light_curves(axis=ax[0], cm=colorMarker[i], zorder=zorder)
            try:
                xBins, yBins = lightCurve.bin_light_curve()
                peakPhases, peakFluxes = lightCurve.get_peaks(axis=ax[1], cm=colorMarker[i], zorder=zorder)
                if peakPhases is None:
                    continue
                header = lightCurve.snVars
                xBinsList.append(xBins)
                yBinsList.append(yBins)
                peaks[snName] = {'peakPhases': peakPhases, 'peakFluxes': peakFluxes}
                headerData[snName] = header
            except TypeError:
                pass
        peaks = pd.DataFrame.from_dict(peaks).transpose()
        headerData = pd.DataFrame.from_dict(headerData).transpose()

        xBinsArray, yBinsArray = np.array(xBinsList), np.array(yBinsList)
        averageLC = np.nanmean(yBinsArray, axis=0)
        errorsLC = np.nanstd(yBinsArray, axis=0)

        if plot is True:
            ax[0].plot(xBinsArray[0], averageLC, 'k-', zorder=1000)
            ax[0].fill_between(xBinsArray[0], averageLC - errorsLC, averageLC + errorsLC, alpha=0.7, zorder=1000)

            plt.xlabel('Phase (days)')
            plt.xlim(-20, 100)
            # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., ncol=1)
            plt.savefig('Figures/' + self.bandName)

        return xBinsArray, yBinsArray, peaks, headerData

    def get_mu(self, headerData):
        muList = headerData.loc[:, ['mu_Snoopy', 'err_mu_Snoopy', 'mu_LCDM']]
        muList = muList.apply(pd.to_numeric)

        return muList

    def plot_mu_vs_peaks(self, muList, peaks):
        labelledMaxima = {}

        fig, ax = plt.subplots(2, 2, sharex='col', sharey='row')
        muPeaksCombined = pd.concat([muList, peaks], axis=1)
        for snName, row in muPeaksCombined.iterrows():
            labelledMaxima[snName] = {}
            if row['peakPhases'].any():
                count = {'first': 0, 'second': 0, 'other': 0}
                for peakPhase, peakFlux in zip(row['peakPhases'], row['peakFluxes']):
                    if -15 < peakPhase < 8:  # First peak
                        ax[1, 0].errorbar(peakPhase, row['mu_Snoopy'], yerr=row['err_mu_Snoopy'], fmt='o', color='#1f77b4', alpha=0.5)
                        ax[1, 1].errorbar(peakFlux,row['mu_Snoopy'], yerr=row['err_mu_Snoopy'], fmt='o', color='#1f77b4', alpha=0.5)
                        labelledMaxima[snName]['firstMaxPhase'] = peakPhase
                        labelledMaxima[snName]['firstMaxFlux'] = peakFlux
                        count['first'] += 1
                    elif 15 < peakPhase < 40:  # Second peak
                        ax[0, 0].errorbar(peakPhase, row['mu_Snoopy'], yerr=row['err_mu_Snoopy'], fmt='o', color='#1f77b4', alpha=0.5)
                        ax[0, 1].errorbar(peakFlux, row['mu_Snoopy'], yerr=row['err_mu_Snoopy'], fmt='o', color='#1f77b4', alpha=0.5)
                        labelledMaxima[snName]['secondMaxPhase'] = peakPhase
                        labelledMaxima[snName]['secondMaxFlux'] = peakFlux
                        count['second'] += 1
                    else:
                        labelledMaxima[snName]['otherMaxPhase'] = peakPhase
                        labelledMaxima[snName]['otherMaxFlux'] = peakFlux
                        count['other'] += 1

                if count['first'] > 1:
                    print("More than one first maximum recorded for {0} in band {1}".format(snName, self.bandName))
                if count['second'] > 1:
                    print("More than one second maximum recorded for {0} in band {1}".format(snName, self.bandName))

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

        labelledMaxima = pd.DataFrame.from_dict(labelledMaxima).transpose()

        return labelledMaxima
