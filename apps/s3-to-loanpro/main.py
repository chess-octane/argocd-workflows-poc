import os
import sys
import json
from tempfile import NamedTemporaryFile
import requests
import boto3

PARAMETERS = {
    "s3BucketName": os.environ.get('S3_BUCKET_NAME'),
    "loanProApiSecretName": os.environ.get('LOANPRO_API_SECRET_NAME'),
    "loanProEntity": os.environ.get('LOANPRO_ENTITY'),
    "loanProImportProgression": os.environ.get('LOANPRO_IMPORT_PROGRESSION'),
    "loanProRejectionType": os.environ.get('LOANPRO_REJECTION_TYPE'),
    "awsRegionName": os.environ.get('AWS_REGION'),
}
BOTO3_SESSION = boto3.session.Session()


def get_secrets():
    client = BOTO3_SESSION.client(service_name='secretsmanager', region_name=PARAMETERS["awsRegionName"])
    secrets = client.get_secret_value(SecretId=PARAMETERS['loanProApiSecretName'])

    print('Secrets loaded')

    if 'SecretString' in secrets:
        return json.loads(secrets['SecretString'])

    return secrets['SecretBinary']


def download_s3_file(bucket_name, object_name: str, local_file_path: str):
    print("Downloading file {} from S3 bucket {}".format(object_name, bucket_name))
    client = BOTO3_SESSION.client('s3')

    with open(local_file_path, 'wb') as file:
        client.download_fileobj(bucket_name, object_name, file)


def send_loanpro_file(file_path: str, entity: str, api_key: str, tenant_id: str):
    file_name = os.path.basename(file_path)

    import_response = requests.post(
        "https://roadrunner.simnang.com/api/public/api/1/data/import/upload/{entity}".format(entity=entity),
        data={
            "fileName": file_name,
            "importProgression": PARAMETERS['loanProImportProgression'],
            "validationType": PARAMETERS['loanProRejectionType']
        },
        headers={
            "Authorization": "Bearer {api_key}".format(api_key=api_key),
            "Autopal-Instance-ID": tenant_id,
        },
    )
    print("Import response from LoanPro: %s %s", import_response.status_code, import_response.text)
    import_response.raise_for_status()

    response_json = json.loads(import_response.text)

    loanpro_file_id = response_json["d"]["id"]
    loanpro_upload_url = response_json["d"]["url"]
    print("Created import file ID={file_id} in LoanPro".format(file_id=loanpro_file_id))

    upload_response = requests.put(
        loanpro_upload_url,
        files = {'file': (file_name, open(file_path, 'rb'), 'text/csv')}
    )

    print("Upload response from LoanPro: %s %s", upload_response.status_code)
    upload_response.raise_for_status()


def run(file_list):
    secrets = get_secrets()

    print('{} files to upload.'.format(len(file_list)))

    for s3_object_name in file_list:
        with NamedTemporaryFile() as local_tmp_file:
            download_s3_file(PARAMETERS["s3BucketName"], s3_object_name.strip(), local_tmp_file.name)
            send_loanpro_file(local_tmp_file.name, PARAMETERS['loanProEntity'], secrets['api_key'], secrets['tenant_id'])


if __name__ == "__main__":
    try:
        file_list = sys.argv[1].split("\n")
        run(file_list)
    except IndexError:
        raise Exception("Missing input arguments")
