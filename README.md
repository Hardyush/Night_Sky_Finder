# Night Sky Estimator using Astrometry.net

This Python tool uploads night sky images to [Astrometry.net](http://nova.astrometry.net), solves them, and estimates when and where the photo was taken based on celestial patterns. It supports multiple image formats and processes them automatically.

---

##  Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Hardyush/Night_Sky_Finder.git
cd Night_Sky_Finder
```
### 2. Get a free API key
    
- Go to nova.astrometry.net
- Create a free account
- Go to your user profile
- Copy your API key

### 3. Create a `.env` file

Inside the project folder, create a file named `.env` and add the following line:
```init
ASTROMETRY_API_KEY=place_your_api_key_here
```

### 4. Add images to `Images/` folder

Supported file types:
- jpeg, jpg
- png
- fits

You can add as many images as you like

### 5. Run the script

```bash
python astrometry_api.py
```

Results will be saved in a file called `results.txt`

---

# Sample Output

Each image returns:
- Submission and job ID in terminal
- Estimated Celestial Data in terminal
- Any Errors
- Estimated date and time

Example output in `results.txt`
```yaml
===== test1.jpeg =====
Lat 80°, Lon 30°, Time 20:00 UTC, Altitude: 88.00°
Lat 80°, Lon 0°, Time 22:00 UTC, Altitude: 88.00°
Lat 80°, Lon 60°, Time 18:00 UTC, Altitude: 88.00°
Lat 80°, Lon 90°, Time 16:00 UTC, Altitude: 88.00°
Lat 80°, Lon 120°, Time 14:00 UTC, Altitude: 88.00°
```

---

# Notes

- The script waits for Astrometry.net to solve each job, so processing time depends on server load and image quality.
- If an image fails, an error will be logged and the script will continue with the next file.

---

# License

This project is open-source and free to use. Attribution is appreciated.