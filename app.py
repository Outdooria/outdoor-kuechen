import os
import replicate
from flask import Flask, render_template, request, jsonify
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-kitchen", methods=["POST"])
def upload_kitchen():
    try:
        file = request.files["image"]
        image_stream = BytesIO(file.read())

        # Hintergrund entfernen mit bria/remove-background
        output = replicate.run(
            "bria/remove-background:k2n7712895rm80cr1zxb6bkm20",
            input={"image": image_stream}
        )

        print("Replicate-Ausgabe:", output)

        if isinstance(output, list) and len(output) > 0:
            return jsonify({"url": output[0]})
        elif isinstance(output, str):
            if output.startswith("http"):
                return jsonify({"url": output})
            elif output.strip().startswith("iVBOR"):
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
    app.run(host="0.0.0.0", port=5000, debug=True)
