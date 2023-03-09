docker run \
    --env S3_BUCKET_NAME=ch-airflow-dev \
    --env LOANPRO_API_SECRET_NAME=airflow/connections/loanpro-api \
    --env LOANPRO_ENTITY=Payments \
    --env LOANPRO_IMPORT_PROGRESSION=auto \
    --env LOANPRO_REJECTION_TYPE=line \
    --env AWS_REGION=$AWS_REGION \
    --env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    octane/s3-to-loanpro test.csv
