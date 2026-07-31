import os
import uuid

from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        url = request.form.get("url", "").strip()
        download_type = request.form.get("format", "video")

        if not url:
            return render_template(
                "index.html",
                error="Please enter a YouTube URL."
            )

        unique_name = str(uuid.uuid4())

        try:

            # -----------------------------
            # AUDIO DOWNLOAD
            # -----------------------------
            if download_type == "audio":

                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(
                        DOWNLOAD_FOLDER,
                        unique_name + ".%(ext)s"
                    ),
                    "noplaylist": True,
                    "quiet": False,

                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }

            # -----------------------------
            # VIDEO DOWNLOAD
            # -----------------------------
            else:

                ydl_opts = {
                    "format": "bv*+ba/b",
                    "merge_output_format": "mp4",

                    "outtmpl": os.path.join(
                        DOWNLOAD_FOLDER,
                        unique_name + ".%(ext)s"
                    ),

                    "noplaylist": True,

                    "quiet": False,
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                ydl.extract_info(url, download=True)

            # -----------------------------
            # FIND DOWNLOADED FILE
            # -----------------------------
            downloaded_file = None

            for file in os.listdir(DOWNLOAD_FOLDER):

                if file.startswith(unique_name):

                    downloaded_file = os.path.join(
                        DOWNLOAD_FOLDER,
                        file
                    )

                    break

            if downloaded_file is None:

                return render_template(
                    "index.html",
                    error="Download failed. File not found."
                )

            return send_file(
                downloaded_file,
                as_attachment=True,
                download_name=os.path.basename(downloaded_file)
            )

        except Exception as e:

            return render_template(
                "index.html",
                error=str(e)
            )

    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return render_template(
        "index.html",
        error="Page not found."
    ), 404


@app.errorhandler(500)
def server_error(e):
    return render_template(
        "index.html",
        error="Internal Server Error."
    ), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )