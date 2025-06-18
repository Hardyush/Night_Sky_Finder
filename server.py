from flask import Flask, request, jsonify
from astrometry_api import get_session, upload_image

app = Flask(__name__)

@app.route("/solve", methods=["POST"])
def solve_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    session = get_session()
    if not session:
        return jsonify({"error": "Login failed"}), 500

    upload_response = upload_image(image_file, session)
    return jsonify(upload_response)