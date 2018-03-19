import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
import copy


def read_optical_fitted_table(filename):
    """ Read in optical parameters as a pandas DataFrame. 
    And set SN_Names as row indexes and the other parameters as column headers. """
    data = pd.read_csv(filename, header=None, delim_whitespace=True, comment='#')
    data.columns = data.iloc[0]
    data = data.reindex(data.index.drop(0))
    data = data.set_index('SN_name')

    return data


def common_optical_nir_sn(nirPeaks, opticalData, bandName):
    """Find the common supernova names between optical and NIR
    and create new DataFrames that contain only information for common SNe."""
    nirPeaks = copy.deepcopy(nirPeaks)
    opticalData = copy.deepcopy(opticalData)

    nirNames = nirPeaks.index
    opticalNames = opticalData.index
    names = opticalNames.intersection(nirNames)
    nirPeaks = nirPeaks.loc[names]
    if not names.equals(opticalNames):
        print("Some NIR SNe don't have optical data in %s" % bandName)
        opticalData = opticalData.loc[names]

    return nirPeaks, opticalData


class CompareOpticalAndNIR(object):
    def __init__(self, opticalDataFilename, nirPeaks, bandName):
        self.opticalData = read_optical_fitted_table(opticalDataFilename)
        self.nirPeaks = nirPeaks
        self.bandName = bandName

        # Add AbsMag column
        self.opticalData = self.opticalData.astype('float')
        self.opticalData['AbsMagB'] = self.opticalData['mB'] - self.opticalData['mu_Snoopy']

        # Add nirpeaks flux ratio
        self.nirPeaks['SecondMaxMag - FirstMaxMag'] = self.nirPeaks['secondMaxMag'] - self.nirPeaks['firstMaxMag']

    def nir_peaks_vs_optical_params(self):
        nirPeaks = self.nirPeaks[['SecondMaxMag - FirstMaxMag', 'secondMaxPhase']]
        opticalData = self.opticalData[['AbsMagB', 'x0', 'x1', 'c']]
        nirPeaks, opticalData = common_optical_nir_sn(nirPeaks, opticalData, self.bandName)

        fig, ax = plt.subplots(nrows=len(opticalData.columns), ncols=len(nirPeaks.columns), sharex='col', sharey='row')
        fig.subplots_adjust(wspace=0, hspace=0)
        for i, f in enumerate(opticalData.columns):
            for j, p in enumerate(nirPeaks.columns):
                ax[i, j].scatter(nirPeaks[p], opticalData[f], alpha=0.6, marker='.')
                if i == len(opticalData.columns) - 1:
                    ax[i, j].set_xlabel(p)
                if j == 0:
                    ax[i, j].set_ylabel(f, rotation=0)
                ax[i, j].yaxis.set_major_locator(plt.MaxNLocator(4))
                ax[i, j].tick_params(labelleft='off')
                # ax[i, j].yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))
                ax[i, j].yaxis.set_label_coords(-0.2, 0.2)
        fig.subplots_adjust(left=0.2, right=0.98)
        fig.suptitle(self.bandName)
        plt.savefig("Figures/%s_opticalParams_vs_NIR_peaks" % self.bandName)

    def plot_parameters(self, fig=None, ax=None, i=0, band='', figinfo=None):
        xname, yname, xlabel, ylabel, savename, sharey = figinfo

        # Only plot supernovae for which we have both optical and NIR data
        if xname in self.opticalData or yname in self.opticalData:
            nirPeaks, opticalData = common_optical_nir_sn(self.nirPeaks, self.opticalData, self.bandName)
        else:
            nirPeaks, opticalData = copy.deepcopy(self.nirPeaks), copy.deepcopy(self.opticalData)

        # Get data
        if xname in self.nirPeaks:
            x = nirPeaks[xname].values.astype('float')
        elif xname in self.opticalData:
            x = opticalData[xname].values.astype('float')
        else:
            raise ValueError("Invalid x parameter: {}".format(xname))
        if yname in self.nirPeaks:
            y = nirPeaks[yname].values.astype('float')
        elif yname in self.opticalData:
            y = opticalData[yname].values.astype('float')
        else:
            raise ValueError("Invalid y parameter: {}".format(yname))

        # Remove NaNs
        notNan = ~np.isnan(x)
        x = x[notNan]
        y = y[notNan]
        notNan = ~np.isnan(y)
        x = x[notNan]
        y = y[notNan]

        # Choose axis labels
        if not xlabel:
            xlabel = xname
        if not ylabel:
            ylabel = yname
        if not savename:
            savename = "{}_vs_{}".format(yname, xname)

        # Fit trend line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_pred = np.arange(min(x), max(x), 0.1)
        y_pred = slope * x_pred + intercept
        print("{}: {} vs {}".format(band, xname, yname))
        print("Slope: {0}, Intercept: {1}, R: {2}, p-value:{3}".format(slope, intercept, r_value, p_value))

        # Plot yname vs xname
        ax[i].plot(x, y, '.k')
        ax[i].plot(x_pred, y_pred, 'b')
        ax[i].set_ylabel(ylabel)
        ax[-1].set_xlabel(xlabel)
        ax[i].text(0.05, 0.85, band, transform=ax[i].transAxes, fontsize=15)
        if 'mag' in yname.lower() and sharey is False:
            ax[i].invert_yaxis()
        ax[i].text(0.7, 0.15, 'R=%.3f' % r_value, transform=ax[i].transAxes)
        ax[i].text(0.7, 0.05, 'p_value=%.3f' % p_value, transform=ax[i].transAxes)
        fig.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        fig.savefig("Figures/{}.png".format(savename), bbox_inches='tight')

