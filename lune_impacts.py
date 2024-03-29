import codecs, sys, os
from math import ceil
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D  
import matplotlib.pyplot as plt
import numpy as np

# ncols        960
# nrows        640
# xllcorner    180.000000000000
# yllcorner    0.000000000000
# cellsize     480

def read_data(filename, plot):

    with codecs.open(filename, encoding='utf-8-sig') as f:
        data = np.loadtxt(f, skiprows = 5)
        data = np.flip(data,0)
        data[data == -9999] = np.nan
        cell_size = 0.015625
        num_rows = data.shape[0]
        num_cols = data.shape[1]
        xll_corner = 180
        x_max = xll_corner+(num_cols*cell_size) 
        yll_corner = 0
        y_max = yll_corner+(num_cols*cell_size)
        moon_frame = [xll_corner,x_max,yll_corner,y_max]

        if plot is True:
            print(moon_frame)
            plt.figure()
            plt.imshow(data, extent=moon_frame, aspect='auto')
            heatmap = plt.pcolor(data)
            plt.colorbar(heatmap)
            plt.show()

        return data

def apply_mask(dem, mask_matrix, crater_num):

    temp = mask_matrix==crater_num
    temp_dem = np.copy(dem)
    temp_dem[temp==0] = np.nan

    # testing by graphing
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
    max_dim = (int(np.sum(np.count_nonzero(temp, axis=0) > 0)))
    area = np.count_nonzero(temp != 0)
    coords = np.where(temp_dem == np.nanmin(temp_dem))

    return (crater_num, depth, max_dim, area, coords)

def get_crater_topography(dem, mask_matrix, direction, crater_dict):
    # Use subplot to plot all transects in the same output
    cols = 8
    rows = ceil(len(crater_dict) / cols)

    for index, key in enumerate(crater_dict):
        if index == 16:
            temp = mask_matrix==index+1
            temp_dem = np.copy(dem)
            temp_dem[temp==0] = np.nan
            profile_location = np.where(temp_dem == np.nanmin(temp_dem))
            # plt.subplot(rows, cols, index + 1) 
            if direction == 'WE':
                plt.plot(temp_dem[profile_location[0][0]])
            elif direction == 'NS':
                plt.plot(temp_dem[:,profile_location[1][0]])
    if direction == 'WE':         
        plt.title('Transects en Ouest-Est')
    elif direction == 'NS':
        plt.title('Transects en Nord-Sud')
    plt.show()

    return None

def get_crater_data():
    crater_data = {}
    terrain = read_data('lune_impacts.asc', False)
    masque = read_data('lune_masque.asc', False)

    for i in range(1,int(np.max(masque) + 1)):
        curr_num, curr_depth, curr_len, curr_num_cells, curr_coords = apply_mask(terrain,masque,i)
        curr_radius = np.sqrt((curr_num_cells*480**2)/np.pi)
        crater_data[curr_num] = curr_depth, curr_len, round(curr_radius, 2), curr_coords, 

    return crater_data

def plot_crater_data(crater_data):

    profondeurs = []
    rayons = []
    for k,v in crater_data.items():
        profondeurs.append(v[0])
        rayons.append(v[2])

    plt.scatter(
        profondeurs, 
        rayons,
        color='black',
        label='Rayon de cratère'
    )

    plt.scatter(profondeurs[16], rayons[16], color='red', label='Max.')
    plt.scatter(profondeurs[48], rayons[48], color='green', label='Moyen')
    plt.scatter(profondeurs[96], rayons[96], color='blue', label='Min.')

    p = np.polyfit(profondeurs, np.log(rayons), 1)
    # Convert the polynomial back into an exponential
    a = np.exp(p[1])
    b = p[0]
    depths_fitted = np.linspace(np.min(profondeurs), np.max(profondeurs), 1111)
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
    plt.grid()
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
    plt.xlabel ('Rayon du cratère (m)', fontsize=16)
    plt.ylabel ('Rayon du corps impactant (m) ', fontsize=16)
    plt.title('Rayon du corps impactant en fonction du rayon du cratère')
    plt.grid()
    plt.show()
        
    return None

def calculate_impactor_radius(crater_radius, planet_radius, print_data):
    impactor_radius = (crater_radius**4/planet_radius)**(1/3)
    if print_data:
        print("The impactor radius was : " + str(round(impactor_radius,2)) + " metres.")
    return impactor_radius

def compute_crater_bounds(dem, crater_dict, crater_num):

    centre_row = crater_dict[crater_num][3][0][0]
    centre_col = crater_dict[crater_num][3][1][0]
    max_row = centre_row + int(0.75*crater_dict[crater_num][1])
    min_row = centre_row - int(0.75*crater_dict[crater_num][1])
    left_col = centre_col - int(0.75*crater_dict[crater_num][1])
    right_col = centre_col + int(0.75*crater_dict[crater_num][1])

    if min_row < 0:
        min_row = 0

    return dem[min_row:max_row,left_col:right_col], (min_row, max_row, left_col, right_col), crater_num

def crater_plot_3d(dem, crater_limits, crater_num, save):

    # recompute grid coords based on curr grid size
    print(crater_limits)
    cell_size = 0.015625
    plt.style.use('_mpl-gallery')
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = np.linspace(crater_limits[1]*cell_size, crater_limits[0]*cell_size, num=dem.shape[0])
    x = np.linspace(180+crater_limits[2]*cell_size, 180+crater_limits[3]*cell_size, num= dem.shape[1])
    (x,y) = np.meshgrid(x,y)
    ax.plot_surface(x,y,np.flip(dem,0),rstride=1,cstride=1)
    ax.contour(x, y, np.flip(dem,0), 
               zdir='z', 
               offset=crater_limits[1]*cell_size-crater_limits[0]*cell_size, 
               cmap='coolwarm')
    ax.set_box_aspect((1,1,0.25))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Elevation (m)')
    plt.title('Cratère numéro ' + str(crater_num))
    if save == True:
        if not os.path.exists('projections_3D'):
            os.makedirs('projections_3D')
        plt.tight_layout()
        plt.rcParams.update({'font.size': 3})
        plt.rcParams["figure.figsize"] = [24,24]
        plt.savefig('projections_3D/cratère_'+str(crater_num)+'.png', dpi=1000)
        plt.close()
    else:
        plt.show()

def main(argv):
    r_earth = 6371000
    r_moon = 1738000

    calculate_impactor_radius(600, r_earth, True)
    calculate_impactor_radius(75000, r_earth, True)

    craters = get_crater_data()
    # plot_crater_data(craters)
    # print(craters)
    terrain = read_data('lune_impacts.asc', False)
    masque = read_data('lune_masque.asc', False)

    # get_crater_topography(terrain, masque, 'WE', craters)
    # get_crater_topography(terrain, masque, 'NS', craters)
    # analyse_crater_radius(craters, 1738000)
    # crater_to_plot = compute_crater_bounds(terrain, craters, 17)
    # crater_plot_3d(crater_to_plot[0], crater_to_plot[1], crater_to_plot[2])

    for i in range(1, 112):
        crater_to_plot = compute_crater_bounds(terrain, craters, i)
        crater_plot_3d(crater_to_plot[0], crater_to_plot[1], crater_to_plot[2], True)

if __name__ == "__main__":
	main(sys.argv)