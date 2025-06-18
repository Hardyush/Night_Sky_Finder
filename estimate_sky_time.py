from skyfield.positionlib import position_of_radec
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u
import argparse
import json
import requests



def estimate_time(job_id):
    url = f'http://nova.astrometry.net/api/jobs/{job_id}/calibration'
    response = requests.get(url)
    calibration_data = response.json()
    print(json.dumps(calibration_data, indent=2))
    ra_deg = calibration_data['ra']
    dec_deg = calibration_data['dec']
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate date/time from Astrometry result.json")
    parser.add_argument("json", help="Path to the result.json file")
    args = parser.parse_args()

    estimate_time(args.json)