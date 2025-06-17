from skyfield.api import load, utc
from skyfield.positionlib import position_of_radec
import numpy as np
import requests
import json
import time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u
import os
from dotenv import load_dotenv

load_dotenv()
ASTROMETRY_API_KEY = os.getenv("ASTROMETRY_API_KEY")

R = requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": "ASTROMETRY_API_KEY"})})
session = R.json()['session']
print(session)
def upload_image(session, image_path):
    url = 'http://nova.astrometry.net/api/upload'
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'request-json': json.dumps({'session': session})}
        response = requests.post(url, data=data, files=files)
        result = response.json()
        if 'subid' in result:
            return result['subid']
        else:
            raise Exception(f"Upload failed: {result.get('errormessage', result)}")

subid = upload_image(session, r"C:\Users\jainv\Pictures\Night Sky\test1.jpeg")
print("Submission ID:", subid)
def wait_for_job(subid):
    status_url = f'http://nova.astrometry.net/api/submissions/{subid}'
    print("Waiting for job to start solving...")
    while True:
        response = requests.get(status_url)
        result = response.json()
        if result['jobs']:
            job_id = result['jobs'][0]
            if job_id:
                return job_id
        time.sleep(40)

job_id = wait_for_job(subid)
print("Job ID:", job_id)
job_info = requests.get(f"http://nova.astrometry.net/api/jobs/{job_id}/info").json()

def get_calibration(job_id):
    url = f'http://nova.astrometry.net/api/jobs/{job_id}/calibration'
    response = requests.get(url)
    return response.json()

calibration_data = get_calibration(job_id)
print(json.dumps(calibration_data, indent=2))

# Step 1: Your input from Astrometry.net
ra_deg = calibration_data['ra']
dec_deg = calibration_data['dec']
ra_hours = ra_deg / 15  # Convert to hours for Skyfield
fov_tolerance_deg = calibration_data['radius']  # from radius

def find_best_location_time(ra_deg, dec_deg, fov_deg):
    # Setup sky coordinate from astrometry
    sky_coord = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')

    # Search range for lat/lon and time
    latitudes = np.arange(-90, 91, 10)  # every 10 degrees
    longitudes = np.arange(-180, 181, 10)

    # Try a few candidate times (e.g. a full night range on a fixed day)
    base_date = '2024-06-01'
    hours = np.arange(0, 24, 1)

    best_matches = []

    for lat in latitudes:
        for lon in longitudes:
            location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
            for h in hours:
                t = Time(f"{base_date} {h:02d}:00:00")
                altaz = sky_coord.transform_to(AltAz(obstime=t, location=location))
                if altaz.alt.deg > 60:  # target is high in sky
                    best_matches.append((lat, lon, h, altaz.alt.deg))

    return sorted(best_matches, key=lambda x: -x[3])  # highest altitude first

candidates = find_best_location_time(ra_deg, dec_deg, fov_tolerance_deg)
for lat, lon, hour, alt in candidates[:5]:
    print(f"Lat {lat}°, Lon {lon}°, Time {hour}:00 UTC, Altitude: {alt:.2f}°")