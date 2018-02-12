import os
import numpy as np
import matplotlib.pyplot as plt
from scripts.population_statistics import PopulationStatistics
from scripts.helpers import get_filenames
from chainconsumer import ChainConsumer

from scipy.optimize import minimize
import celerite
from celerite import terms


def get_data(band):
    filenameList, scriptDir = get_filenames(band)
    popStats = PopulationStatistics(filenameList, band)
    xBinsArray, yBinsArray, peaks, headerData = popStats.get_binned_light_curves(plot=False, bin_size=4)
    x = xBinsArray[0]  # Binned epochs
    y = np.nanmean(yBinsArray, axis=0)  # Average Light curve
    yerr = np.nanstd(yBinsArray, axis=0)  # Stand Deviation of all light curves
    cov = np.diag(yerr ** 2)  # Covariance matrix (assuming data at different epochs are independent)

    return x, y, yerr, cov


def plot_data(x, y, yerr):
    fig, ax = plt.subplots(1)
    ax.errorbar(x, y, yerr=yerr, fmt='.k')
    ax.invert_yaxis()
    ax.set_title(band)
    ax.set_xlabel('Phase (days)')
    ax.set_ylabel('Abs mag')


def gp_model(x, y, yerr, scriptDir):
    # Set up the GP model
    kernel = terms.RealTerm(log_a=np.log(np.nanvar(y)), log_c=-np.log(10.0))
    gp = celerite.GP(kernel, mean=np.nanmean(y))
    gp.compute(x, yerr)
    print("Initial log-likelihood: {0}".format(gp.log_likelihood(y)))

    # Define a cost function
    def neg_log_like(params, y, gp):
        gp.set_parameter_vector(params)
        return -gp.log_likelihood(y)

    def grad_neg_log_like(params, y, gp):
        gp.set_parameter_vector(params)
        return -gp.grad_log_likelihood(y)[1]

    # Fit for the maximum likelihood parameters
    initial_params = gp.get_parameter_vector()
    bounds = gp.get_parameter_bounds()
    soln = minimize(neg_log_like, initial_params, jac=grad_neg_log_like,
                    method="L-BFGS-B", bounds=bounds, args=(y, gp))
    gp.set_parameter_vector(soln.x)
    print("Final log-likelihood: {0}".format(-soln.fun))

    # Make the maximum likelihood prediction
    t = np.linspace(-10, 100, 500)
    mu, var = gp.predict(y, t, return_var=True)
    std = np.sqrt(var)

    # Plot the data
    plt.figure()
    color = "#ff7f0e"
    plt.errorbar(x, y, yerr=yerr, fmt=".k", capsize=0)
    plt.plot(t, mu, color=color)
    plt.fill_between(t, mu + std, mu - std, color=color, alpha=0.3, edgecolor="none")
    plt.ylabel(r"$y$")
    plt.xlabel(r"$t$")
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(5))
    plt.title("maximum likelihood prediction")
    plt.gca().invert_yaxis()

    def log_probability(params):
        gp.set_parameter_vector(params)
        lp = gp.log_prior()
        if not np.isfinite(lp):
            return -np.inf
        return gp.log_likelihood(y) + lp

    import emcee

    initial = np.array(soln.x)
    ndim, nwalkers = len(initial), 32
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability)

    print("Running burn-in...")
    p0 = initial + 1e-8 * np.random.randn(nwalkers, ndim)
    p0, lp, _ = sampler.run_mcmc(p0, 500)

    print("Running production...")
    sampler.reset()
    sampler.run_mcmc(p0, 2000)

    # Plot the data.
    plt.errorbar(x, y, yerr=yerr, fmt=".k", capsize=0)

    # Plot 24 posterior samples.
    
    samples = sampler.flatchain
    for s in samples[np.random.randint(len(samples), size=24)]:
        gp.set_parameter_vector(s)
        mu = gp.predict(y, t, return_cov=False)
        plt.plot(t, mu, color=color, alpha=0.3)

    plt.ylabel(r"$y$")
    plt.xlabel(r"$t$")
    plt.xlim(-10, 100)
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(5))
    plt.title(r"{0} posterior predictions".format(band).replace('_', '-'))
    plt.savefig(os.path.join(scriptDir, '../Figures/%s posterior predictions' % band))

    names = gp.get_parameter_names()
    c = ChainConsumer()
    c.add_chain(samples, parameters=('log(a)', 'log(c)'))
    c.plotter.plot(filename=os.path.join(scriptDir, '../Figures/{0}_param_contours.png'.format(band)))


if __name__ == '__main__':
    bandList = ['H_band', 'J_Band', 'K_band', 'Y_Band']
    scriptDir = os.path.dirname(os.path.realpath(__file__))

    for band in bandList:
        x, y, yerr, cov = get_data(band)

        # plot_data(x, y, yerr)

        gp_model(x, y, yerr, scriptDir)

    plt.show()
