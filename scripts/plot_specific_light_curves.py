import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .fit_light_curve import LightCurve
from .optical_parameters import read_optical_fitted_table, common_optical_nir_sn
from .helpers import get_filenames


def get_filename_from_snname(band, snNameList):
    filePathListAll, scriptDir = get_filenames(band)
    filenameList = []
    for snName in snNameList:
        for filepath in filePathListAll:
            if snName in filepath:
                filenameList.append(filepath)
                break  # Only take first sn found with same name
    return filenameList


def plot_specific_light_curves(filenameList=(), colorMarker=None, bin_size=1, band='Y', nirPeaks=None, opticalDataFilename=None, individualplots=False, title=None, savename=None, offsetFlag=True, plotSpline=False, fig_in=None, ax_in=None, linestyle='-'):
    if filenameList == 'common_optical_nir':
        opticalFlag = True
        opticalData = read_optical_fitted_table(opticalDataFilename)
        nirPeaks, opticalData = common_optical_nir_sn(nirPeaks, opticalData, band)
        snNameList = nirPeaks.index
        filePathListAll, scriptDir = get_filenames(band)
        filenameList = []
        x1List = []

        # Remove NaNs
        notNan = ~np.isnan(nirPeaks['secondMaxMag'].values.astype('float'))
        snNameList = snNameList[notNan]
        # Plot just 5 SN:
        # snNameList = ['sn2006D', 'sn2007af', 'sn2007as', 'sn2007le', 'sn2008bc']

        for snName in snNameList:
            for filepath in filePathListAll[::-1]:
                if snName in filepath:
                    filenameList.append(filepath)
                    x1List.append(float(opticalData['x1'][snName]))
                    break  # Only take first sn found with same name
        sortedbyx1list = sorted(list(zip(filenameList, x1List)), key=lambda x: x[1])
        filenameList = list(zip(*sortedbyx1list))[0]
        if len(filenameList) != len(snNameList):
            raise IndexError("There is a problem with a filename not existing!")


    else:
        opticalFlag = False

    if not os.path.isfile(filenameList[0]):
        filenameList = get_filename_from_snname(band, snNameList=filenameList)

    if not individualplots:
        if fig_in is None:
            fig, ax = plt.subplots(1, figsize=(12, 10))
        else:
            fig, ax = fig_in, ax_in

    zorder = 200
    offset = 0
    for i, filename in enumerate(filenameList):
        snName = os.path.basename(filename).split('_')[0]

        lightCurve = LightCurve(filename, bin_size=bin_size, interpKind='cubic')

        if opticalFlag:
            if individualplots:
                label = "{} x1={}, c={}".format(band, opticalData['x1'][snName], opticalData['c'][snName])
            else:
                label = "{}: x1={}, c={}".format(snName, opticalData['x1'][snName], opticalData['c'][snName])
            print(label, filename)
        else:
            label = snName
        # if band == 'J':
        #     label = None

        if not individualplots:
            zorder -= 1
            lightCurve.plot_light_curves(axis=ax, cm=colorMarker[i], zorder=zorder, label=label, plot_spline=plotSpline, offset=offset, linestyle=linestyle)
            if opticalFlag:
                maxmag = nirPeaks['secondMaxMag'][snName]
                maxphase = nirPeaks['secondMaxPhase'][snName]
                ax.plot((maxphase, maxphase), (maxmag+offset-1, maxmag+offset+1), color='k')
                ax.text(x=maxphase+1, y=maxmag+offset-0.2, s="{}".format(maxphase))
            if offsetFlag:
                offset += 2
        else:
            if fig_in is None:
                fig, ax = plt.subplots(1)
                title = "{}: {}".format(band, snName)
                savename = "Figures/individual_plots/%s/%s.png" % (band, snName)
            else:
                fig, ax = fig_in[snName], ax_in[snName]
                title = "{}".format(snName)
                if not os.path.exists('Figures/individual_plots'):
                    os.makedirs('Figures/individual_plots')
                savename = "Figures/individual_plots/%s.png" % snName
            lightCurve.plot_light_curves(axis=ax, cm=('k', 'o'), zorder=0, label=label, plot_spline=True, offset=0, linestyle=linestyle)
            if opticalFlag:
                maxmag = nirPeaks['secondMaxMag'][snName]
                maxphase = nirPeaks['secondMaxPhase'][snName]
                ax.plot((maxphase, maxphase), (maxmag+offset-0.5, maxmag+offset+0.5), color='b', linestyle=linestyle)
                ax.text(x=maxphase+1, y=maxmag+offset+0.1, s="{}".format(maxphase))
            ax.set_title(title)
            ax.set_ylabel('Abs mag')
            ax.set_xlabel('Phase (days)')
            if fig_in is None:
                ax.invert_yaxis()
            ax.legend()
            fig.savefig(savename)

    if not individualplots:
        ax.set_title("{}: {}".format(band, title))
        ax.set_ylabel('Abs mag - offset')
        ax.set_xlabel('Phase (days)')
        if fig_in is None:
            ax.invert_yaxis()
        ax.legend()  # loc=2, bbox_to_anchor=(1.01, 1))
        fig.savefig("Figures/%s_%s.png" % (band, savename), bbox_inches='tight')
