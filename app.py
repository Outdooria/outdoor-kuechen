import os
import replicate
from flask import Flask, render_template, request, jsonify
from io import BytesIO

app = Flask(__name__)

# Startseite
@app.route("/")
def index():
    return render_template("index.html")


# Küche hochladen + Hintergrund entfernen
@app.route("/upload-kitchen", methods=["POST"])
def upload_kitchen():
    try:
        file = request.files["image"]

        # Bild als Datei-Stream (file-like object) umwandeln
        image_stream = BytesIO(file.read())

        # Replicate rembg aufrufen
        output = replicate.run(
            "cjwbw/rembg:1.4.1",
            input={"image": image_stream}
        )

        print("Replicate-Ausgabe:", output)

        # Rückgabe-Formate prüfen
        if isinstance(output, list) and len(output) > 0:
            return jsonify({"url": output[0]})
        elif isinstance(output, str):
            if output.startswith("http"):
                return jsonify({"url": output})
            elif output.strip().startswith("iVBOR"):  # PNG Base64
                return jsonify({"base64": output})
            else:
                return jsonify({"error": "Unbekanntes Format", "raw": output}), 500
        else:
            return jsonify({"error": "Fehler beim Freistellen", "raw": str(output)}), 500

    except Exception as e:
        import traceback
        print("Upload-Kitchen Fehler:", traceback.format_exc())
        return jsonify({"error": "Serverfehler", "details": str(e)}), 500


if __name__ == "__main__":
    # Lokal starten
    app.run(host="0.0.0.0", port=5000, debug=True)
