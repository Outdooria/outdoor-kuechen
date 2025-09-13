import os
import replicate
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Startseite
@app.route("/")
def index():
    return render_template("index.html")


# Küche hochladen + Hintergrund entfernen
@app.route("/upload-kitchen", methods=["POST"])
def upload_kitchen():
    file = request.files["image"]

    # Das rembg-Modell von Replicate aufrufen
    # Wichtig: REPLICATE_API_TOKEN muss in Render unter Environment Variables gesetzt sein!
    output = replicate.run(
        "cjwbw/rembg:1.4.1",
        input={"image": file}
    )

    # Replicate liefert in der Regel eine URL zurück
    if isinstance(output, list) and len(output) > 0:
        return jsonify({"url": output[0]})
    elif isinstance(output, str):
        return jsonify({"url": output})
    else:
        return jsonify({"error": "Fehler beim Freistellen"}), 500


if __name__ == "__main__":
    # Lokaler Start, auf Render läuft gunicorn (siehe Procfile)
    app.run(host="0.0.0.0", port=5000, debug=True)
