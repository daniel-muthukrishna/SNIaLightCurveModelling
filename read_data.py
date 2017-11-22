import numpy as np
import pandas as pd


def read_data(filename):
    with open(filename, 'r') as FileObj:
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

    data = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=12, names=columnNames)

    return fileVars, data



if __name__ == '__main__':
    read_data('NIR_Lowz_data/K_band/sn1998bu__U_69_B_9_CfA_K.txt')
