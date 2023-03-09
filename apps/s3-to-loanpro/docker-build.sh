docker build \
    --build-arg NPM_CONFIG_REGISTRY=$NPM_CONFIG_REGISTRY \
    --build-arg NPM_CONFIG__AUTH=$NPM_CONFIG__AUTH \
    --build-arg PIP_INDEX_URL="https://$ARTIFACTORY_USER:$ARTIFACTORY_PASS@octanelending.jfrog.io/octanelending/api/pypi/pypi/simple" \
    -t octane/s3-to-loanpro .
