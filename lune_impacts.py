import codecs
import matplotlib.pyplot as plt
import numpy as np
import sys

# ncols        960
# nrows        640
# xllcorner    180.000000000000
# yllcorner    0.000000000000
# cellsize     480

def plot_data(filename, plot):

    with codecs.open(filename, encoding='utf-8-sig') as f:
        data = np.loadtxt(f, skiprows = 5)
        # print(data)

        data[data == -9999] = np.nan
        cell_size = 0.015625
        num_rows = data.shape[0]
        num_cols = data.shape[1]
        xll_corner = 180
        x_max = xll_corner+(num_cols*cell_size) 
        yll_corner = 0
        y_max = yll_corner+(num_cols*cell_size)

        if plot is True:
            moon_frame = [xll_corner,x_max,yll_corner,y_max]
            plt.figure()
            # recalculate the x ticks based on cell size
            plt.imshow(data)
            plt.show()

        return data

def apply_mask(dem, mask_matrix, crater_num):

    temp = mask_matrix==crater_num
    temp_dem = np.copy(dem)
    temp_dem[temp==0] = np.nan

    # testing for graph
    # print(temp)
    # plt.figure()
    # plt.imshow(mask_matrix==crater_num)
    # plt.imshow(dem)
    # plt.show()

    # print(temp)
    # sys.exit(0)


    min_depth = np.nanmin(temp_dem)
    max_height = np.nanmax(temp_dem)
    depth = max_height - min_depth
    max_dim = (int(np.sum(np.count_nonzero(temp, axis=0) > 0)))*480
    area = np.count_nonzero(temp != 0)

    return (crater_num, depth, max_dim, area)
    
crater_data = {}

terrain = plot_data('lune_impacts.asc', False)

masque = plot_data('lune_masque.asc', False)

for i in range(1,int(np.max(masque)+ 1)):
    temp_num, temp_depth, temp_len, temp_area = apply_mask(terrain,masque,i)
    crater_data[temp_num] = temp_depth, temp_len, temp_area

print(crater_data)

areas = []
for k,v in crater_data.items():
    areas.append(v[2])

print(areas)