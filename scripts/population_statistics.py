import matplotlib.pyplot as plt
import numpy as np

from .fit_light_curve import LightCurve


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
        ax[0].fill_between(xBinsArray[0], averageLC - errorsLC, averageLC + errorsLC, alpha=0.7, zorder=1000)

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
                        count += 1
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
