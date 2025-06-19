from accessors import cosmosaccessor
from accessors import blobstoreaccessor
import ffmpeg_handler
'''
1. Read the message to identify upload_id
2. Query cosmos to find information about it - the number of chunks required
3. Call blobstore to stitch the video
4. Make its state "STITCHED" in DB
4. Call ffmpeg to start processing it, and upload the partitions to blobstore
6. Make its state "COMPLETED" in DB
7. Move this information to "videos" table so that it can be served
'''
def process_message(message):
    try :
        upload_id = b"".join(message.body).decode("utf-8").strip()
        if not upload_id:
            raise ValueError("Upload ID is missing")
        upload_info = cosmosaccessor.read("uploads", upload_id)
        if not upload_info or not upload_info.get("chunks"):
            raise ValueError("Upload ID is invalid, missing chunks information")
        chunks = upload_info.get("chunks")
        blobstoreaccessor.finish_raw_upload(upload_id, chunks)
        markVideo(upload_info, upload_info.get("_etag"), "STITCHED")
        ffmpeg_handler.handle(upload_id, blobstoreaccessor.generate_blob_sas(upload_id))
        upload_info = cosmosaccessor.read("uploads", upload_id)
        markVideo(upload_info, upload_info.get("_etag"), "COMPLETED")
        moveVideo(upload_info)

    except Exception as e :
        print(e)
        # push to DLQ


def markVideo(upload_info, etag, status):
    upload_info.update({
        "upload_status": status,
        "ttl": 60 * 60 * 24 * 7,
    })
    cosmosaccessor.put("uploads", etag, upload_info)


def moveVideo(upload_info):
    upload_id = upload_info["upload_id"]
    upload_info.update({
        "video_id": upload_id,
        "upload_id": None,
        "upload_status": None,
        "chunks": None,
        "chunk_size": None,
        "_rid": None,
        "_self": None,
        "_etag": None,
        "_attachments": None,
    })
    cosmosaccessor.create("videos", upload_info)
