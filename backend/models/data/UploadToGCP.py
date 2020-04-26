from google.cloud import storage

bucket_name = "ieor185-274323.appspot.com"

source_file_name = "health_prediction.csv"
destination_blob_name = "health_prediction.csv"
storage_client = storage.Client.from_service_account_json('key.json')
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(destination_blob_name)

blob.upload_from_filename(source_file_name)

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)

source_file_name = "state_prediction.csv"
destination_blob_name = "state_prediction.csv"
storage_client = storage.Client.from_service_account_json('key.json')
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(destination_blob_name)

blob.upload_from_filename(source_file_name)

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)