from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.identity import DefaultAzureCredential
import base64
from datetime import datetime, timedelta


AZURE_BLOB_URL = "https://ytstorage2.blob.core.windows.net"
AZURE_CONTAINER_NAME_RAW = 'yt-video-raw'
AZURE_CONTAINER_NAME_PROCESSED = 'yt-video-processed'
AZURE_BLOB_NAME = '<video_id>.mp4'

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(AZURE_BLOB_URL, credential)
raw_container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME_RAW)
processed_container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME_PROCESSED)

def finish_raw_upload(upload_id : str, num_chunks : int) :
    block_ids = []
    for i in range(num_chunks):
        block_id = base64.b64encode(f"{i:06}".encode()).decode()
        block_ids.append(block_id)

    blob_client = raw_container_client.get_blob_client(upload_id)
    blob_client.commit_block_list(block_ids)

def upload_processed_blob(blob_path : str, data):
    processed_container_client.upload_blob(name=blob_path, data=data, overwrite=True)

def get_sas_token(blob_id):
    start_time = datetime.utcnow()
    expiry_time = start_time + timedelta(hours=1)
    delegation_key = blob_service_client.get_user_delegation_key(start_time, expiry_time)
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=AZURE_CONTAINER_NAME_RAW,
        blob_name=blob_id,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time,
        user_delegation_key=delegation_key
    )
    return sas_token
