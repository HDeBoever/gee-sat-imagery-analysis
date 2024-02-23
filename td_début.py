import math as m
import numpy as np
import geopy.distance
import matplotlib.pyplot as plt
from misfit import calc_misfit
from mpl_toolkits.basemap import Basemap

# Exploraoin des paramètres en x,y,z et t
def calculate_hypocentre(stations):
	prev_misfit = 10
	result = {}
	for i in range(-2000,-1000):
		for j in range(-3400,3000):
			for k in range(-35000,-30000):
				curr_event = {'X':i, 'Y':j, 'Z':-k, 't':-5.1}
				curr_misfit = calc_misfit(stations, curr_event,6500)
				if curr_misfit < prev_misfit:
					result[curr_misfit] = (i,j,k,-5.1)
					prev_misfit = curr_misfit
					# print('Curr misfit : ' + str(curr_misfit))
					# print(i,j,k)
				else:
					break
	# (0.06449304787805835, (-1606, 2236, -34997, -5.1))
	return result.popitem()

def plot_carte(stations, hypocentre):
	
	# La zone d'intérêt est dans la zone UTM 38S, donc EPSG 4471 ou 4470
	plt.figure(figsize=(12,12))
	map = Basemap(
		llcrnrlon=44.9,
		llcrnrlat=-13.3,
		urcrnrlon=46,
		urcrnrlat=-12.3,
		epsg=4470,
	)
	
	for s,data in stations.items():
		# print(s, data['lon'], data['lat'])
		plt.plot(data['lon'], data['lat'],'ro')
		# plt.text(data['lon'], data['lat'], s)
		plt.annotate(
			s, # text
			(data['lon'],data['lat']), # these are the coordinates to position the label
			textcoords="offset points", # how to position the text
			xytext=(0,10), # distance from text to points (x,y)
			ha='left',
			color='w',
		)
		
	# Ajouter l'hypocentre :
	plt.plot(hypocentre[1], hypocentre[0],'*',label='epicentre')
	plt.annotate('Epicentre : 2019 00:58:08.01',(hypocentre[1], hypocentre[0]), textcoords='offset points', xytext=(0,-15), color='w', ha='center')
	
	# draw parallels and meridians.
	# labels = [left,right,top,bottom]
	
	parallels = np.arange(-13.5,-12,0.2)
	map.drawparallels(parallels,linewidth=0.18, color= 'w', labels=[False,True,False,False])
	
	meridians = np.arange(44.5,46.7,0.2)
	map.drawmeridians(meridians,linewidth=0.18, color= 'w', labels=[False,False,False,True])

	# Faire appel à #http://server.arcgisonline.com/arcgis/rest/services pour avoir des images de meilleure résolution
	map.arcgisimage(service='World_Imagery', xpixels = 2000, verbose= True)
	plt.title('Carte des sismometres au large de Mayotte')
	plt.show()

	return None

def distance_hypocentrale(hypocentre, stations):
	result = []
	surface_distances = []
	vertical_distances = []
	distances_hypocentrales = []
	# print(hypocentre)
	epicentre = (hypocentre[0], hypocentre[1])
	depth = hypocentre[2] 
	
	# Ajuster pour avoir les profondeurs relatives au fond marin pour chaque sismomètre
	for k,v in stations.items():
		curr_lat = v['lat']
		curr_lon = v['lon']
		curr_station_coords = (curr_lat, curr_lon)
		surface_distances.append((k,geopy.distance.geodesic(epicentre, curr_station_coords).meters))
		vertical_distances.append((k,depth+3120-v['Z']))
		
	# Faire la distance avec pythagore
	for i in range(0, len(surface_distances)):
		distances_hypocentrales.append((surface_distances[i][0], np.sqrt(surface_distances[i][1]**2 + vertical_distances[i][1]**2)))
	
	return distances_hypocentrales

def calculate_local_amplitudes( amplitudes, distances_hypocentrales):
	
	print(distances_hypocentrales)
	local_mags = []
	a = 1.0
	b = 1.306
	c = 0.0346
	d = -2.877
	
	for element in distances_hypocentrales:
		# convertir de nm en metres
		curr_amp = amplitudes[element[0]]
		curr_m_wood_anderson = a*np.log10(curr_amp) + b*np.log10(element[1]/1000) + c*element[1]/1000 + d
		print(curr_m_wood_anderson)
		local_mags.append((element[0], f'Magnitude locale : {curr_m_wood_anderson:.3f}'))
		
	print(local_mags)
	return local_mags

def convert_event_to_coords(stations, event):
	
	event_lat = event['X']
	event_lon = event['Y']
	event_depth = event['Z']
	ref_station_lat = stations['MOCE']['lat']
	ref_station_lon = stations['MOCE']['lon']
	ref_station_depth = -3120
	
	m_per_deg_lat=1852*60
	m_per_deg_lon=m_per_deg_lat*m.cos(ref_station_lon*m.pi/180)
	
	deg_lat_per_m=1/(1852*60)
	deg_lon_per_m= 1/m_per_deg_lon
	
	hypocentre_lat = ref_station_lat + deg_lat_per_m*event_lat
	hypocentre_lon = ref_station_lon - deg_lon_per_m*event_lon
	hypocentre_depth = ref_station_depth + event_depth
	print('MOCE', ref_station_lat, ref_station_lon)
	print('HYPOCENTRE',hypocentre_lat, hypocentre_lon, hypocentre_depth)
	
	return hypocentre_lat,hypocentre_lon, hypocentre_depth

def main():
	
	# établir les différents temps d'arrivée des ondes sur chaque station à partir de la figure 1.
	stations={
		'MOCE':dict(lat=-12-48.44/60, lon=45+38.06/60, Z=-3120, t=0),
		'MONE':dict(lat=-12-39.91/60, lon=45+48.22/60, Z=-3510, t=1.63),
		'MONN':dict(lat=-12-29.59/60, lon=45+33.46/60, Z=-3180, t=2.28),
		'MONO':dict(lat=-12-39.08/60, lon=45+23.51/60, Z=-1600, t=1.86),
		'MOSE':dict(lat=-12-57.75/60, lon=45+49.19/60, Z=-3520, t=2.05),
		'MOSO':dict(lat=-13-01.07/60, lon=45+27.51/60, Z=-2520, t=2.08),
	}
	
	amplitudes={'MOCE':1960, 'MONE':3180, 'MONN':1140, 'MONO':4100,'MOSE':2320, 'MOSO':1760}
	ref_station=stations['MOCE'].copy()
	m_per_deg_lat=1852*60
	
	for station in stations.values():
		m_per_deg_lon=m_per_deg_lat*m.cos(station['lat']*m.pi/180)
		station['Y']=(station['lat']-ref_station['lat'])*m_per_deg_lat
		station['X']=(station['lon']-ref_station['lon'])*m_per_deg_lon
		station['Z']=station['Z']-ref_station['Z']

	print('Stations :')

	for s,v in stations.items():
		print(s,v)
	
	event_test={'X':-1606, 'Y':2236., 'Z':-34997., 't':-5.1}
	misfit=calc_misfit(stations, event_test, 6500)
	print(f'Test Event:{event_test}, misfit={misfit:.3f}')
	
	print('Using gradient method, starting at test event')
	# result = calculate_hypocentre(stations)
	# misfit = result[0]
	# best_fit = {'X':result[1][0], 'Y':result[1][1], 'Z':result[1][2], 't':-5.1}
	# séisme = best_fit
	hypocentre = convert_event_to_coords(stations, event_test)
		
	# plot_carte(stations, hypocentre)
	# print(f'Best fit event={best_fit}, misfit={misfit:.3f}')
	
	misfit = 0.06449304787805835
	best_fit = {'X':-1606, 'Y':2236., 'Z':-34997., 't':-5.1}
	
	d_hypo = distance_hypocentrale(hypocentre, stations)
	calculate_local_amplitudes(amplitudes,  d_hypo)

if (__name__ == "__main__"):
	main()
