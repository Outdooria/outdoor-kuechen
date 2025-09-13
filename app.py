import os, uuid, time
import replicate, requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXT = {"png","jpg","jpeg"}
CLEANUP_OLDER_THAN_SECONDS = 24*3600

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_TOKEN:
    raise RuntimeError("Bitte REPLICATE_API_TOKEN als Umgebungsvariable setzen.")

replicate_client = replicate.Client(api_token=REPLICATE_TOKEN)
MODEL = replicate_client.models.get("cjwbw/rembg")
VERSION = MODEL.versions[0]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

def cleanup_old_files():
    now = time.time()
    for p in Path(UPLOAD_FOLDER).iterdir():
        try:
            if now - p.stat().st_mtime > CLEANUP_OLDER_THAN_SECONDS:
                p.unlink()
        except Exception:
            pass

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    cleanup_old_files()
    terrasse = request.files.get("terrasse")
    kueche = request.files.get("kueche")

    if not terrasse:
        return jsonify({"error":"Terrassenbild fehlt"}), 400
    if not kueche:
        return jsonify({"error":"Küchenbild fehlt"}), 400
    if not (allowed_file(terrasse.filename) and allowed_file(kueche.filename)):
        return jsonify({"error":"Ungültiges Dateiformat"}), 400

    t_name = f"{uuid.uuid4().hex}_{secure_filename(terrasse.filename)}"
    k_name = f"{uuid.uuid4().hex}_{secure_filename(kueche.filename)}"
    terrasse_path = os.path.join(UPLOAD_FOLDER, t_name)
    kueche_path = os.path.join(UPLOAD_FOLDER, k_name)
    terrasse.save(terrasse_path)
    kueche.save(kueche_path)

    try:
        with open(kueche_path, "rb") as f:
            output_url = VERSION.predict(image=f)
    except Exception as e:
        return jsonify({"error": "Fehler bei Freistellung: " + str(e)}), 500

    try:
        resp = requests.get(output_url, stream=True, timeout=30)
        resp.raise_for_status()
        freed_name = k_name.rsplit(".",1)[0] + "_frei.png"
        freed_path = os.path.join(UPLOAD_FOLDER, freed_name)
        with open(freed_path, "wb") as out:
            for chunk in resp.iter_content(chunk_size=8192):
                out.write(chunk)
    except Exception as e:
        return jsonify({"error":"Fehler beim Herunterladen des freigestellten Bildes: "+str(e)}), 500

    return jsonify({
        "terrasse": f"/{terrasse_path.replace(os.sep, '/')}",
        "kueche": f"/{freed_path.replace(os.sep, '/')}"
    })

if __name__ == "__main__":
    app.run(debug=True)
