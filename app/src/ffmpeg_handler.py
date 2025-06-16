from accessors import blobstoreaccessor
import subprocess
import tempfile
import os

def handle(upload_id):
    # TODO : Add a SAS token at the end of this URL.
    source_url = "https://ytstorage2.blob.core.windows.net/yt-video-raw/" + upload_id
    with tempfile.TemporaryDirectory() as output_dir:
        command = [
            "ffmpeg",
            "-i", source_url,
            "-preset", "fast",
            "-g", "48",
            "-sc_threshold", "0",
            "-map", "0:v",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-f", "hls",
            "-start_number", "0",
            "-hls_time", "6",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", os.path.join(output_dir, "output_%04d.ts"),
            f"{output_dir}/output.m3u8"
        ]

        subprocess.run(command, check=True)

        for file_name in os.listdir(output_dir):
            local_path = os.path.join(output_dir, file_name)
            blob_path = f"{upload_id}/{file_name}"

            with open(local_path, "rb") as data:
                blobstoreaccessor.upload_processed_blob(blob_path, data=data)