from flask import Flask, jsonify, send_file, abort, render_template, send_from_directory
from flask_cors import CORS
import os
from mimetypes import guess_type
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ✅ Fix CORS Issues
CORS(app, supports_credentials=True, origins=["http://localhost:8000"])

# ✅ Allow Preflight Requests
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8000"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# ✅ Base directory for all images
BASE_PATH = "/home/ubuntu/Capturesque/Images"

@app.route('/getJS/<fnam>')
def getpage(fnam):
    return send_from_directory('static', secure_filename(fnam))

@app.route('/api/images', methods=['GET'])
def get_folders():
    try:
        folders = [folder for folder in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, folder))]
        return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch folders: {str(e)}"}), 500

@app.route('/api/images/<path:foldername>', methods=['GET'])
def get_all_images_recursive(foldername):
    # 🔁 Replace _ with / to support frontend path format like Feature_Dusk
    safe_parts = [secure_filename(part) for part in foldername.replace('_', '/').split('/')]
    base_folder_path = os.path.join(BASE_PATH, *safe_parts)

    if not os.path.exists(base_folder_path) or not os.path.isdir(base_folder_path):
        return jsonify({"error": "Folder not found"}), 404

    try:
        images = []
        for root, _, files in os.walk(base_folder_path):
            for file in files:
                if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, BASE_PATH)
                    rel_folder = os.path.dirname(rel_path).replace('\\', '/')
                    encoded_rel_folder = '/'.join([secure_filename(part) for part in rel_folder.split('/')])
                    filename = secure_filename(file)

                    images.append({
                        "id": filename,
                        "name": filename,
                        "url": f"http://150.230.138.173:8087/api/image/{encoded_rel_folder}/{filename}",
                        "thumbnail": f"http://150.230.138.173:8087/api/image/{encoded_rel_folder}/{filename}",
                        "download": f"http://150.230.138.173:8087/api/download/{encoded_rel_folder}/{filename}"
                    })

        if not images:
            return jsonify({"message": "No images found in this folder or its subfolders."}), 200

        return jsonify(images)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch images: {str(e)}"}), 500


@app.route('/api/folders/<path:parent_folder>', methods=['GET'])
def get_subfolders(parent_folder):
    safe_parts = [secure_filename(part) for part in parent_folder.split('/')]
    folder_path = os.path.join(BASE_PATH, *safe_parts)

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    try:
        subfolders = [sf for sf in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, sf))]
        return jsonify({"subfolders": subfolders})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch subfolders: {str(e)}"}), 500

@app.route('/api/image/<path:foldername>/<filename>', methods=['GET'])
def get_image(foldername, filename):
    safe_parts = [secure_filename(part) for part in foldername.split('/')]
    folder_path = os.path.join(BASE_PATH, *safe_parts)
    file_path = os.path.join(folder_path, secure_filename(filename))

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return jsonify({"error": "Image not found"}), 404

    try:
        mimetype, _ = guess_type(file_path)
        return send_file(file_path, mimetype=mimetype if mimetype else 'application/octet-stream')
    except Exception as e:
        return jsonify({"error": f"Failed to fetch image: {str(e)}"}), 500

@app.route('/api/download/<path:foldername>/<filename>', methods=['GET'])
def download_image(foldername, filename):
    safe_parts = [secure_filename(part) for part in foldername.split('/')]
    folder_path = os.path.join(BASE_PATH, *safe_parts)
    file_path = os.path.join(folder_path, secure_filename(filename))

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return jsonify({"error": "Image not found"}), 404

    try:
        return send_file(file_path, as_attachment=True, conditional=True)
    except Exception as e:
        return jsonify({"error": f"Failed to download image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8087)
