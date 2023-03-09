docker run \
    --env SFTP_CREDENTIALS_SECRET_NAME=airflow/connections/speedpay-ftp \
    --env SFTP_FOLDER=/ \
    --env SFTP_FILE_NAME=EXPORT_ \
    --env S3_BUCKET_NAME=ch-airflow-dev \
    --env OUTPUT_FILE_PATH=/fileList.txt \
    --env AWS_REGION=$AWS_REGION \
    --env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    octane/sftp-to-s3
