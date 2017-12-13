import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class LightCurve(object):
    def __init__(self, filename):
        self.filename = filename
        self.snVars, self.data = self.get_data()

    def get_data(self):
        with open(self.filename, 'r') as FileObj:
            lines = FileObj.readlines()

        snName = lines[0].split()[1]
        fileVars = {'snName': snName}
        for line in lines[:10]:
            if line[0] != '#':
                valuesStr, keysStr = line.split(' # ')
                keys = keysStr.replace('(', '', 1).rsplit(')', 1)[0].split(',')
                values = valuesStr.split()
                for i in range(len(keys)):
                    fileVars[keys[i]] = values[i]

        header = lines[11].split('|')
        columnNames = [col.strip('#').strip() for col in header]

        data = pd.read_csv(self.filename, header=None, delim_whitespace=True, skiprows=12, names=columnNames, comment='#')

        return fileVars, data

    def plot_light_curves(self):
        data = self.data
        label = os.path.basename(self.filename)
        if not data['Phase(T_Bmax)'].empty:
            plt.errorbar(data['Phase(T_Bmax)'], data['Abs mag'], yerr=data['Error Abs mag'], fmt='o', label=label.split('_')[0], zorder=1)


        # plt.figure()
        # plt.errorbar(data['Phase(T_Bmax)'], data['App mag'], yerr=data['Error App mag'], fmt='o')

    def bin_light_curve(self):
        phase = self.data['Phase(T_Bmax)'].values
        absMag = self.data['Abs mag'].values
        xBins = np.linspace(-20, 100, 61)
        yBinned = np.interp(x=xBins, xp=phase, fp=absMag, left=np.NaN, right=np.NaN)

        return xBins, yBinned


def get_filenames(band):
    directory = os.path.join('NIR_Lowz_data', band)
    filenameList = os.listdir(directory)
    filePathList = [os.path.join(directory, f) for f in filenameList]

    return filePathList


def main():
    bandList = ['H_band', 'J_Band', 'K_band', 'Y_Band']
    for band in bandList:
        xBinsList, yBinnedList = [], []
        plt.figure()
        plt.title(band)
        filenameList = get_filenames(band)
        for filename in filenameList:
            lightCurve = LightCurve(filename)
            lightCurve.plot_light_curves()
            try:
                xBins, yBinned = lightCurve.bin_light_curve()
                xBinsList.append(xBins)
                yBinnedList.append(yBinned)
            except TypeError:
                pass
        plt.xlabel('Phase')
        plt.ylabel('Abs mag')
        plt.xlim(-20, 100)
        plt.gca().invert_yaxis()
        xBinsArray, yBinnedArray = np.array(xBinsList), np.array(yBinnedList)
        averageLC = np.nanmean(yBinnedArray, axis=0)
        errorsLC = np.nanstd(yBinnedArray, axis=0)
        plt.plot(xBinsArray[0], averageLC, 'k-', zorder=10)
        plt.fill_between(xBinsArray[0], averageLC-errorsLC, averageLC+errorsLC, alpha=0.7, zorder=10)

        # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., ncol=1)
    plt.show()


if __name__ == '__main__':
    main()
