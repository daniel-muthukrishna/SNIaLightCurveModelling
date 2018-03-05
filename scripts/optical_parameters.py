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
        nirPeaks = self.nirPeaks[['secondMaxFlux', 'secondMaxPhase']]
        opticalData = self.opticalData[['mB', 'x0', 'x1', 'c']]
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

    def x1_vs_second_max_phase(self, fig=None, ax=None, i=0, band=''):
        x = self.nirPeaks['secondMaxPhase'].values.astype('float')
        y = self.opticalData['x1'].values.astype('float')
        yerr = self.opticalData['x1_err'].values.astype('float')
        notNan = ~np.isnan(x)
        x = x[notNan]
        y = y[notNan]
        yerr = yerr[notNan]

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_pred = np.arange(min(x), max(x), 0.1)
        y_pred = slope * x_pred + intercept
        print("Slope: {0}, Intercept: {1}, R: {2}, p-value:{3}".format(slope, intercept, r_value, p_value))

        plt.figure()
        plt.errorbar(x, y, yerr=yerr, fmt='.k')
        plt.plot(x_pred, y_pred, 'b')
        plt.xlabel('NIR Second maximum phase (days)')
        plt.ylabel('Optical Stretch, x1')
        plt.title(self.bandName)
        plt.savefig("Figures/%s_x1_vs_2nd_max_phase.png" % self.bandName)

        if fig is not None:
            ax[i].errorbar(x, y, yerr=yerr, fmt='.k')
            ax[i].plot(x_pred, y_pred, 'b')
            ax[i].set_ylabel('{} optical x1'.format(band))
            ax[-1].set_xlabel('NIR Second maximum phase (days)')
            fig.subplots_adjust(hspace=0)
            plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
            fig.savefig("Figures/x1_vs_2nd_max_phase.png", bbox_inches='tight')

        # def lnlike(theta, x, y, yerr):
        #     m, b, lnf = theta
        #     model = m * x + b
        #     inv_sigma2 = 1.0 / (yerr ** 2 + model ** 2 * np.exp(2 * lnf))
        #     return -0.5 * (np.sum((y - model) ** 2 * inv_sigma2 - np.log(inv_sigma2)))
        #
        # def lnprior(theta):
        #     m, b, lnf = theta
        #     if -np.inf < m < np.inf and -np.inf < b < np.inf and -np.inf < lnf < np.inf:
        #         return 0.0
        #     return -np.inf
        #
        # def lnprob(theta, x, y, yerr):
        #     lp = lnprior(theta)
        #     if not np.isfinite(lp):
        #         return -np.inf
        #     return lp + lnlike(theta, x, y, yerr)
        #
        # ndim, nwalkers = 3, 100
        # pos = [1 + 1e-4 * np.random.randn(ndim) for i in range(nwalkers)]
        # import emcee
        # sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(x, y, yerr))
        # sampler.run_mcmc(pos, 500)
        # samples = sampler.chain[:, 50:, :].reshape((-1, ndim))
        #
        # import corner
        # fig = corner.corner(samples, labels=["$m$", "$b$", "$\ln\,f$"])
        # fig.savefig("%s_triangle.png" % self.bandName)
        #
        # for m, b, lnf in samples[np.random.randint(len(samples), size=100)]:
        #     plt.plot(xl, m * xl + b, color="b", alpha=0.1)