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

    # Aufruf des rembg-Modells von Replicate
    output = replicate.run(
        "cjwbw/rembg:1.4.1",
        input={"image": file}
    )

    # Debug-Ausgabe im Render-Log
    print("Replicate-Ausgabe:", output)

    # Verschiedene Rückgabe-Formate von Replicate abfangen
    if isinstance(output, list) and len(output) > 0:
        return jsonify({"url": output[0]})
    elif isinstance(output, str):
        if output.startswith("http"):
            return jsonify({"url": output})
        else:
            return jsonify({"base64": output})
    else:
        return jsonify({"error": "Fehler beim Freistellen"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
