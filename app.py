from flask import Flask, request, send_file
import requests
import subprocess
import uuid
import os

app = Flask(__name__, static_folder="/tmp", static_url_path="")  # <- Statik dizin eklendi

def wrap_text(text, max_line_length=60):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_line_length:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

@app.route("/add_text", methods=["POST"])
def add_text():
    data = request.json
    image_url = data.get("image_url")
    text = data.get("text", "No text provided.")

    if not image_url:
        return {"error": "image_url is required"}, 400

    input_filename = f"{uuid.uuid4()}.jpg"
    output_filename = f"{uuid.uuid4()}_out.jpg"

    img = requests.get(image_url)
    with open(input_filename, "wb") as f:
        f.write(img.content)

    text = wrap_text(text)
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_filename,
        "-vf",
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
        "text='{}':"
        "fontcolor=white:"
        "fontsize=24:"
        "box=1:boxcolor=black@0.6:boxborderw=15:"
        "x=(w-text_w)/2:"
        "y=h-text_h-50:"
        "line_spacing=10:"
        "bordercolor=black:borderw=1".format(
            text.replace(":", "\\:").replace("'", "\\'").replace(",", "\\,").replace("=", "\\=")
        ),
        "-frames:v", "1",
        "-q:v", "2",
        "-y", output_filename
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": "ffmpeg failed", "details": str(e)}, 500

    return send_file(output_filename, mimetype="image/png")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "No file part in the request"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join("/tmp", filename)
    file.save(filepath)

    public_url = f"https://{request.host}/{filename}"
    return {"url": public_url}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
