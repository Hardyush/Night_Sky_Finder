import requests
import json
import os
from dotenv import load_dotenv
import time
import argparse
from estimate_sky_time import estimate_time

load_dotenv()
ASTROMETRY_API_KEY = os.getenv("ASTROMETRY_API_KEY")

def get_session():
    R = requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": "ASTROMETRY_API_KEY"})})
    session = R.json()['session']
    print("Session Id:", session)
def upload_image(image_path):
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    session = get_session()
    print(f"[→] Uploading {image_path} to Astrometry.net...")
    url = 'http://nova.astrometry.net/api/upload'
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'request-json': json.dumps({'session': session})}
        response = requests.post(url, data=data, files=files)
    result = response.json()
    if "subid" not in result:
        raise Exception(f"Upload failed: {result.get('errormessage')}")
    subid = result["subid"]
    print(f"[✓] Submission ID: {subid}")

    status_url = f'http://nova.astrometry.net/api/submissions/{subid}'
    print("Waiting for job to start solving...")
    while True:
        response = requests.get(status_url)
        result = response.json()
        if result['jobs']:
            job_id = result['jobs'][0]
            if job_id:
                print(f"[✓] Job ID: {job_id}")
                break
        time.sleep(40)

    job_info = requests.get(f"http://nova.astrometry.net/api/jobs/{job_id}/info").json()
    with open("result.json", "w") as f:
      json.dump(job_info, f, indent=2)
    return job_id

if __name__ == "__main__":
    image_dir = "Images"
    results_file = "results.txt"
    
    if not os.path.exists(image_dir):
        print(f"❌ Folder '{image_dir}' does not exist.")
        exit(1)

    with open(results_file, "w") as f_out:
        for filename in os.listdir(image_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".fits")):
                image_path = os.path.join(image_dir, filename)
                print(f"\n📷 Processing: {image_path}")

                try:
                    job_id = upload_image(image_path)
                    print(f"✅ Job ID for {filename}: {job_id}")

                    print(f"⏳ Estimating sky time for job {job_id}...")
                    result = estimate_time(job_id)

                    # Write to results.txt
                    f_out.write(f"===== {filename} =====\n")
                    f_out.write(result + "\n\n")
                    print(f"📝 Results saved for {filename}")

                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")