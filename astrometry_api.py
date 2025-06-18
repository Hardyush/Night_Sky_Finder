import requests
import json
import os
from dotenv import load_dotenv
import time
import argparse

load_dotenv()
ASTROMETRY_API_KEY = os.getenv("ASTROMETRY_API_KEY")

def upload_image(image_path, output_json="result.json"):
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
    with open("result.json", "w") as f:
        json.dump(job_info, f, indent=2)

    def get_calibration(job_id):
        url = f'http://nova.astrometry.net/api/jobs/{job_id}/calibration'
        response = requests.get(url)
        return response.json()

    calibration_data = get_calibration(job_id)
    print(json.dumps(calibration_data, indent=2))
    # Write result.json
    with open(output_json, "w") as f:
        json.dump(calibration_data, f, indent=2)
    print(f"[✓] Saved result to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload sky image to Astrometry.net")
    parser.add_argument("image", help="Path to the sky image file (e.g., photo.jpg)")
    parser.add_argument("--out", default="result.json", help="Path to save result.json")
    args = parser.parse_args()

    upload_image(args.image, args.out)