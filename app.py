import os
import base64
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from PIL import Image
import io
import json
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

MAX_SIZE_MB = 5
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload PNG, JPG, JPEG, GIF, WEBP, or BMP."}), 400

    file_bytes = file.read()
    if len(file_bytes) > MAX_SIZE_MB * 1024 * 1024:
        return jsonify({"error": f"File too large. Max size is {MAX_SIZE_MB}MB."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()

    # Convert BMP to PNG if needed
    if ext == "bmp":
        img = Image.open(io.BytesIO(file_bytes))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        file_bytes = buf.getvalue()

    pil_image = Image.open(io.BytesIO(file_bytes))

    prompt = """Analyze this electronic schematic image and extract all components and their values.

Return a JSON object with this exact structure:
{
  "components": [
    {"type": "Resistor", "label": "R1", "value": "10kOhm"},
    {"type": "Capacitor", "label": "C1", "value": "100nF"},
    ...
  ],
  "summary": "Brief one-sentence description of the circuit",
  "component_count": 5
}

Rules:
- Include every component you can identify (resistors, capacitors, inductors, ICs, transistors, diodes, connectors, voltage sources, etc.)
- Use the label from the schematic if visible (R1, C2, U1, etc.)
- Use the value from the schematic if visible, otherwise write "Not labeled"
- Return ONLY valid JSON, no extra text, no markdown fences."""

    try:
        response = model.generate_content([prompt, pil_image])
        result_text = response.text.strip()

        # Strip markdown code fences if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()

        result = json.loads(result_text)
        return jsonify({"success": True, "data": result})

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
