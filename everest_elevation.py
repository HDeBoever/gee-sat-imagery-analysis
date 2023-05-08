import ee

service_account = 'gee-service-account@gee-experimentation.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'private-key.json')
ee.Initialize(credentials)

dem = ee.Image('USGS/SRTMGL1_003')
xy = ee.Geometry.Point([86.9250, 27.9881])
elev = dem.sample(xy, 30).first().get('elevation').getInfo()
print('Mount Everest elevation (m):', elev)
