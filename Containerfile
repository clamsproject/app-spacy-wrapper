# Use the same base image version as the clams-python python library version
FROM ghcr.io/clamsproject/clams-python:1.3.2
# See https://github.com/orgs/clamsproject/packages?tab=packages&q=clams-python for more base images
# IF you want to automatically publish this image to the clamsproject organization,
# 1. you should have generated this template without --no-github-actions flag
# 1. to add arm64 support, change relevant line in .github/workflows/container.yml
#     * NOTE that a lots of software doesn't install/compile or run on arm64 architecture out of the box
#     * make sure you locally test the compatibility of all software dependencies before using arm64 support
# 1. use a git tag to trigger the github action. You need to use git tag to properly set app version anyway

################################################################################
# DO NOT EDIT THIS SECTION
ARG CLAMS_APP_VERSION
ENV CLAMS_APP_VERSION ${CLAMS_APP_VERSION}
################################################################################

################################################################################
# This is duplicate from the base image Containerfile
# but makes sure the cache directories are consistent across all CLAMS apps

# https://github.com/openai/whisper/blob/ba3f3cd54b0e5b8ce1ab3de13e32122d0d5f98ab/whisper/__init__.py#L130
ENV XDG_CACHE_HOME='/cache'
# https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables#hfhome
ENV HF_HOME="/cache/huggingface"
# https://pytorch.org/docs/stable/hub.html#where-are-my-downloaded-models-saved
ENV TORCH_HOME="/cache/torch"

RUN mkdir /cache ; rm -rf /root/.cache ; ln -s /cache /root/.cache
################################################################################

################################################################################
# clams-python base images are based on debian distro
# install more system packages as needed using the apt manager
################################################################################

################################################################################
# main app installation
COPY ./ /app
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

# default command to run the CLAMS app in a production server
CMD ["python3", "app.py", "--production"]
################################################################################
