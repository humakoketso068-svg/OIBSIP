from flask import Flask, jsonify, request, send_from_directory

import analysis

app = Flask(__name__, static_folder="public", static_url_path="")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/dashboard")
def dashboard():
    return jsonify(analysis.dashboard())


@app.get("/api/compare")
def compare():
    regions = request.args.getlist("region")
    return jsonify(analysis.compare(regions))


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})
