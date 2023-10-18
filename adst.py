import codecs
import matplotlib.pyplot as plt
import numpy as np

# NCOLS 609
# NROWS 432
# XLLCORNER 14.7637502905
# YLLCORNER 37.5679167877
# CELLSIZE 0.000833
# NODATA_VALUE  -9999.0000

def get_slope(nd_data, axis, cellsize):
    if axis == 'x':
        slope_array = data[:,:-1] - data[:,1:]
        print(slope_array)
        return slope_array/cellsize
    elif axis == 'y':
        slope_array = data[:-1,:] - data[1:,:]
        print(slope_array)
        return slope_array/cellsize
    else:
        print(data[:-1,:-1] - data[1:,1:])
        return (data[1:,1:] - data[:-1,:-1])/cellsize

def plot_data(plot):

    with codecs.open('MNT-Etna.asc', encoding='utf-8-sig') as f:
        data = np.loadtxt(f, skiprows = 6)
        # print(data)

        data[data == -9999] = np.nan

        cell_size = 0.000833
        num_rows = data.shape[0]
        num_cols = data.shape[1]
        xll_corner = 14.7637502905
        x_max = xll_corner+(num_cols*cell_size) 
        yll_corner = 37.5679167877
        y_max = yll_corner+(num_cols*cell_size)

        etna_frame = [xll_corner,x_max,yll_corner,y_max]

        if plot is True:

            plt.figure()

            # recalculate the x ticks based on cell size
            plt.imshow(data, cmap='grey', extent=etna_frame)
            plt.xticks(np.arange(xll_corner, xll_corner+(num_cols*cell_size), 0.1))
            plt.yticks(np.arange(yll_corner, yll_corner+(num_cols*cell_size), 0.1))
            plt.xlabel ('Longitude', fontsize=12)
            plt.ylabel ('Latitude', fontsize=12)
            plt.show()

        return data

def plot_slopes(data, slope_matrix, shadow):

    slope_matrix[slope_matrix == -9999] = np.nan

    cell_size = 0.000833
    num_rows = slope_matrix.shape[0]
    num_cols = slope_matrix.shape[1]
    xll_corner = 14.7637502905
    x_max = xll_corner+(num_cols*cell_size) 
    yll_corner = 37.5679167877
    y_max = yll_corner+(num_cols*cell_size)

    etna_frame = [xll_corner,x_max,yll_corner,y_max]

    plt.imshow(slope_matrix, cmap='Greys_r', extent=etna_frame, alpha=shadow)
    # plt.imshow(data, extent=etna_frame)
    plt.xticks(np.arange(xll_corner, xll_corner+(num_cols*cell_size), 0.1))
    plt.yticks(np.arange(yll_corner, yll_corner+(num_cols*cell_size), 0.1))
    plt.xlabel ('Longitude', fontsize=12)
    plt.ylabel ('Latitude', fontsize=12)
    plt.show()

data = plot_data(False)

x_slope = get_slope(data, 'x', 0.000833)
y_slope = get_slope(data, 'y', 0.000833)
xy_slope = get_slope(data, 'both', 0.000833)

plot_slopes(data, xy_slope, 0.3)
plot_slopes(data, xy_slope, 0.5)
plot_slopes(data, xy_slope, 1)