import pandas as pd
import matplotlib.pyplot as plt

def read_optical_fitted_table(filename):
    """ Read in optical parameters as a pandas DataFrame. 
    And set SN_Names as row indexes and the other parameters as column headers. """
    data = pd.read_csv(filename, header=None, delim_whitespace=True, comment='#')
    data.columns = data.iloc[0]
    data = data.reindex(data.index.drop(0))
    data = data.set_index('SN_name')

    return data


class CompareOpticalAndNIR(object):
    def __init__(self, opticalDataFilename, nirPeaks, bandName):
        self.opticalData = read_optical_fitted_table(opticalDataFilename)
        self.nirPeaks = nirPeaks
        self.bandName = bandName
        self.common_sn()

    def common_sn(self):
        """Find the common supernova names between optical and NIR 
        and create new DataFrames that contain only information for common SNe."""
        nirNames = self.nirPeaks.index
        opticalNames = self.opticalData.index
        names = opticalNames.intersection(nirNames)
        self.nirPeaks = self.nirPeaks.loc[names]
        if not names.equals(opticalNames):
            print("Some NIR SNe don't have optical data in %s" % self.bandName)
            self.opticalData = self.opticalData.loc[names]

    def nir_peaks_vs_optical_params(self):
        nirPeaks = self.nirPeaks[['firstMaxFlux', 'secondMaxFlux']]
        opticalData = self.opticalData[['mB', 'x1', 'c']]
        fig, ax = plt.subplots(nrows=len(opticalData.columns), ncols=len(nirPeaks.columns), sharex='col', sharey='row')
        fig.subplots_adjust(wspace=0, hspace=0)
        for i, f in enumerate(opticalData.columns):
            for j, p in enumerate(nirPeaks.columns):
                ax[i, j].scatter(nirPeaks[p], opticalData[f], alpha=0.6, marker='.')
                if i == len(opticalData.columns) - 1:
                    ax[i, j].set_xlabel(p)
                if j == 0:
                    ax[i, j].set_ylabel(f)
        plt.savefig("Figures/%s_opticalParams_vs_NIR_peaks" % self.bandName)


