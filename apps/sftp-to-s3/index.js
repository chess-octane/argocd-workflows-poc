const os = require('os');
const fs = require('fs');
const FTPClient = require('ssh2-sftp-client');
const path = require('path');
const {
  SecretsManagerClient,
  GetSecretValueCommand,
} = require('@aws-sdk/client-secrets-manager');
const {S3Client, PutObjectCommand} = require('@aws-sdk/client-s3');

const parameters = {
  sftpCredentialsSecretName: process.env['SFTP_CREDENTIALS_SECRET_NAME'],
  sftpFolder: process.env['SFTP_FOLDER'],
  sftpFileName: process.env['SFTP_FILE_NAME'],
  s3BucketName: process.env['S3_BUCKET_NAME'],
  s3Key: process.env['S3_KEY'] || '',
  outputFilePath: process.env['OUTPUT_FILE_PATH'],
};

const s3Client = new S3Client();
const secretsClient = new SecretsManagerClient();

const getSecrets = async () => {
  const command = new GetSecretValueCommand({
    SecretId: parameters.sftpCredentialsSecretName,
  });
  const data = await secretsClient.send(command);
  return JSON.parse(data.SecretString);
};

const uploadS3File = async (localFilePath, fileName) => {
  const s3Path = path.join(parameters.s3Key, fileName);
  const command = new PutObjectCommand({
    Bucket: parameters.s3BucketName,
    Key: s3Path,
    Body: fs.readFileSync(localFilePath),
  });
  await s3Client.send(command);
  return s3Path;
};

const run = async () => {
  // delete the output file if it exists
  if (fs.existsSync(parameters.outputFilePath)) {
    fs.unlinkSync(parameters.outputFilePath);
  }

  const secrets = await getSecrets();
  const ftpClient = new FTPClient();

  await ftpClient.connect({
    host: secrets['host'],
    username: secrets['username'],
    password: secrets['password'],
    port: parseInt(secrets['port']),
    timeout: 5,
  });

  console.log('Retrieving files from FTP');
  const ftpFileList = await ftpClient.list(parameters.sftpFolder);
  const fileNameList = ftpFileList.map((fileInfo) => fileInfo.name);
  const s3CopiedFiles = [];

  const matchingFileList = fileNameList.filter((fileName) =>
    fileName.includes(parameters.sftpFileName)
  );

  console.log(`Matching files: ${matchingFileList}`);

  for (const matchingFileName of matchingFileList) {
    // download from sFTP
    const filePath = path.join(parameters.sftpFolder, matchingFileName);
    const destinationLocalPath = path.join(os.tmpdir(), matchingFileName);
    console.log(`Downloading files from FTP: ${filePath}`);
    await ftpClient.fastGet(filePath, destinationLocalPath);

    // push to S3 bucket
    console.log(`Uploading file ${destinationLocalPath} to S3`);
    const s3Path = await uploadS3File(destinationLocalPath, matchingFileName);

    // add to processed list
    s3CopiedFiles.push(s3Path);
  }

  // write the output file with the list of files copied to S3
  fs.writeFileSync(parameters.outputFilePath, s3CopiedFiles.join('\n'));

  console.log(`Done. ${s3CopiedFiles.length} files copied to S3.`);

  process.exit(0);
};
run();
