import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats


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

        # Add AbsMag column
        self.opticalData = self.opticalData.astype('float')
        self.opticalData['AbsMagB'] = self.opticalData['mB'] - self.opticalData['mu_Snoopy']

        # Add nirpeaks flux ratio
        self.nirPeaks['SecondMaxMag - FirstMaxMag'] = self.nirPeaks['secondMaxMag'] - self.nirPeaks['firstMaxMag']

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
        nirPeaks = self.nirPeaks[['SecondMaxMag - FirstMaxMag', 'secondMaxPhase']]
        opticalData = self.opticalData[['AbsMagB', 'x0', 'x1', 'c']]
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

    def x1_vs_second_max_phase(self):
        y = self.nirPeaks['secondMaxPhase'].values.astype('float')
        x = self.opticalData['x1'].values.astype('float')
        # yerr = self.opticalData['x1_err'].values.astype('float')
        notNan = ~np.isnan(y)
        x = x[notNan]
        y = y[notNan]
        # yerr = yerr[notNan]

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_pred = np.arange(min(x), max(x), 0.1)
        y_pred = slope * x_pred + intercept
        print("Slope: {0}, Intercept: {1}, R: {2}, p-value:{3}".format(slope, intercept, r_value, p_value))

        plt.figure()
        plt.plot(x, y, '.k')
        plt.plot(x_pred, y_pred, 'b')
        plt.xlabel('2nd max phase')
        plt.ylabel('Optical Stretch, x1')
        plt.title(self.bandName)
        plt.savefig("Figures/%s_x1_vs_2nd_max_phase.png" % self.bandName)

    def plot_parameters(self, fig=None, ax=None, i=0, band='', xname='', yname='', xlabel=None, ylabel=None, savename=None):
        # Get data
        if xname in self.nirPeaks:
            x = self.nirPeaks[xname].values.astype('float')
        elif xname in self.opticalData:
            x = self.opticalData[xname].values.astype('float')
        else:
            raise ValueError("Invalid x parameter: {}".format(xname))
        if yname in self.nirPeaks:
            y = self.nirPeaks[yname].values.astype('float')
        elif yname in self.opticalData:
            y = self.opticalData[yname].values.astype('float')
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
            savename = "{}_vs_{}".format(xname, yname)

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
        if 'mag' in yname.lower():
            ax[i].invert_yaxis()
        fig.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        fig.savefig("Figures/{}.png".format(savename), bbox_inches='tight')

