import os


def get_filenames(band):
    directory = os.path.join('data/NIR_Lowz_data', band)
    filenameList = os.listdir(directory)
    filePathList = [os.path.join(directory, f) for f in filenameList]

    return filePathList


def get_colors_and_markers():
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf', 'k', '#911eb4', '#800000', '#aa6e28']
    markers = ['o', 'v', 'P', '*', 'D', 'X', 'p', '3', 's', 'x', 'p']
    colorMarker = []
    for color in colors:
        for marker in markers:
            colorMarker.append((color, marker))
    return colorMarker
