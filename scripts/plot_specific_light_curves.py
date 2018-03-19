import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .fit_light_curve import LightCurve
from .optical_parameters import read_optical_fitted_table, common_optical_nir_sn
from .helpers import get_filenames


def plot_specific_light_curves(filenameList=(), colorMarker=None, bin_size=1, band='Y', nirPeaks=None, opticalDataFilename=None, ):
    if filenameList == 'common_optical_nir':
        opticalFlag = True
        opticalData = read_optical_fitted_table(opticalDataFilename)
        nirPeaks, opticalData = common_optical_nir_sn(nirPeaks, opticalData, band)
        snNameList = nirPeaks.index
        filePathListAll, scriptDir = get_filenames(band)
        filenameList= []
        for snName in snNameList:
            for filepath in filePathListAll:
                if snName in filepath:
                    filenameList.append(filepath)
                    break  # Only take first sn found with same name
        if len(filenameList) != len(snNameList):
            raise IndexError("There is a problem with a filename not existing!")
    else:
        opticalFlag = False

    fig, ax = plt.subplots(1, figsize=(8, 10))

    zorder = 200
    offset = 0
    for i, filename in enumerate(filenameList):
        snName = os.path.basename(filename).split('_')[0]
        zorder -= 1
        offset += 2

        lightCurve = LightCurve(filename, bin_size=bin_size)

        if opticalFlag:
            label = opticalData['x1'][snName]
            print(label, filename)
        else:
            label = snName

        lightCurve.plot_light_curves(axis=ax, cm=colorMarker[i], zorder=zorder, label=label, plot_spline=False, offset=offset)

    ax.set_title("{}: Light curves with x1 values".format(band))
    ax.set_ylabel('Abs mag - offset')
    ax.set_xlabel('Phase (days)')
    ax.invert_yaxis()
    ax.legend(loc=2, bbox_to_anchor=(1.01, 1))
    fig.savefig("Figures/%s_lightcurves_with_x1_vals_with_offset.png" % band, bbox_inches='tight')
