import codecs, sys
from math import ceil
import matplotlib.pyplot as plt
import numpy as np

# ncols        960
# nrows        640
# xllcorner    180.000000000000
# yllcorner    0.000000000000
# cellsize     480

def plot_data(filename, plot):

    with codecs.open(filename, encoding='utf-8-sig') as f:
        data = np.loadtxt(f, skiprows = 5)
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
            plt.imshow(data, extent=moon_frame, aspect='auto')
            plt.show()

        return data

def apply_mask(dem, mask_matrix, crater_num):

    temp = mask_matrix==crater_num
    temp_dem = np.copy(dem)
    temp_dem[temp==0] = np.nan

    # testing for graph
    # plt.figure()
    # plt.imshow(temp)
    # plt.imshow(temp_dem)
    # plt.colorbar()
    # plt.show()

    # print(temp)
    # print(temp_dem)

    max_depth = np.nanmin(temp_dem)
    max_height = np.nanmax(temp_dem)
    depth = max_height - max_depth
    max_dim = (int(np.sum(np.count_nonzero(temp, axis=0) > 0)))*480
    area = np.count_nonzero(temp != 0)

    return (crater_num, depth, max_dim, area)

def get_crater_topography(dem, mask_matrix, direction, crater_dict):
    # Use subplot to get all the craters
    cols = 8
    rows = ceil(len(crater_dict) / cols)

    if direction == 'WE':        
        for index, key in enumerate(crater_dict):
            temp = mask_matrix==index+1
            temp_dem = np.copy(dem)
            temp_dem[temp==0] = np.nan
            profile = np.where(temp_dem == np.nanmin(temp_dem))
            plt.subplot(rows, cols, index + 1) 
            plt.plot(temp_dem[profile[0][0]])
        plt.title('Transects en Ouest-Est')
        plt.show()
    elif direction == 'NS':
        for index, key in enumerate(crater_dict):
            temp = mask_matrix==index+1
            temp_dem = np.copy(dem)
            temp_dem[temp==0] = np.nan
            profile = np.where(temp_dem == np.nanmin(temp_dem))
            plt.subplot(rows, cols, index + 1) 
            plt.plot(temp_dem[:,profile[1][0]])
        plt.title('Transects en Nord-Sud')
        plt.show()
    return None

def get_crater_data():
    crater_data = {}
    terrain = plot_data('lune_impacts.asc', False)
    masque = plot_data('lune_masque.asc', False)

    for i in range(1,int(np.max(masque)+ 1)):
        curr_num, curr_depth, curr_len, curr_num_cells = apply_mask(terrain,masque,i)
        curr_radius = np.sqrt((curr_num_cells*480**2)/np.pi)
        crater_data[curr_num] = curr_depth, curr_len, round(curr_radius,2)

    return crater_data

def plot_crater_data(crater_data):

    depths = []
    rayons = []
    for k,v in crater_data.items():
        depths.append(v[0])
        rayons.append(v[2])

    plt.scatter(
        depths, 
        rayons,
        color='black',
        label='Rayon de cratère'
    )

    p = np.polyfit(depths, np.log(rayons), 1)
    # Convert the polynomial back into an exponential
    a = np.exp(p[1])
    b = p[0]
    depths_fitted = np.linspace(np.min(depths), np.max(depths), 1111)
    y_fitted = a * np.exp(b * depths_fitted)

    plt.plot(
        depths_fitted, 
        y_fitted, 
        color='darkred', 
        label='Courbe de tendance y = a*e^(x*profondeur)',
        linewidth=0.4,
    )

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.xlabel ('Profondeur de cratère (m)', fontsize=16)
    plt.ylabel ('Rayon du cratère (m) ', fontsize=16)
    plt.title('Rayon de cratère en fonction de la profondeur')
    plt.show()

def analyse_crater_radius(craters, R_planete):

    radii = []
    r_meteorites = []

    # R_crater / R_meteorite = (R_planet/R_meteorite)**(1/4)
    # R_meteorite = (R_crater**4/R_planete)**(1/3)
    for key, value in craters.items():
        crater_radius = value[2]
        R_meteorite = (crater_radius**4/R_planete)**(1/3)
        radii.append(crater_radius)
        r_meteorites.append(R_meteorite)

    plt.scatter(
        radii, 
        r_meteorites,
        color='black',
        label='Cratères lunaires'
    )

    plt.scatter(75000, calculate_impactor_radius(75000, 6371000, False), color = 'red', label='Cratère Chicxulub')
    plt.scatter(600, calculate_impactor_radius(600, 6371000, False), color = 'blue', label='Cratère Barringer')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.xlabel ('Rayon de cratère (m)', fontsize=16)
    plt.ylabel ('Rayon du corps impactant (m) ', fontsize=16)
    plt.title('Rayon du corps impactant en fonction du rayon du cratère')
    plt.show()
        
    return None

def calculate_impactor_radius(crater_radius, planet_radius, print_data):
    impactor_radius = (crater_radius**4/planet_radius)**(1/3)
    if print_data:
        print("The impactor radius was : " + str(round(impactor_radius,2)) + " metres.")
    return impactor_radius

def main(argv):
    r_earth = 6371000
    r_moon = 1738000

    calculate_impactor_radius(600, r_earth, True)
    calculate_impactor_radius(75000, r_earth, True)

    craters = get_crater_data()
    plot_crater_data(craters)

    terrain = plot_data('lune_impacts.asc', True)
    masque = plot_data('lune_masque.asc', True)

    get_crater_topography(terrain, masque, 'WE', craters)
    get_crater_topography(terrain, masque, 'NS', craters)
    analyse_crater_radius(craters, 1738000)

if __name__ == "__main__":
	main(sys.argv)