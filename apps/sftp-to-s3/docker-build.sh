docker build \
    --build-arg NPM_CONFIG_REGISTRY=$NPM_CONFIG_REGISTRY \
    --build-arg NPM_CONFIG__AUTH=$NPM_CONFIG__AUTH \
    -t octane/sftp-to-s3 .
