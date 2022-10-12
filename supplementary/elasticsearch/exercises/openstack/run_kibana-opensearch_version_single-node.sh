#!/bin/bash
#
# Script to start kibana
#

NAME="kibana"

# Name of the docker image to use
VERSION="1.3.4"
IMAGE="opensearchproject/opensearch-dashboards:$VERSION"

# Docker custom options
OPTS+=" -d "
OPTS+=" --restart=unless-stopped "
#OPTS+=" --privileged"
OPTS+=" --net=host"
#OPTS+=" -v /sys/fs/cgroup:/sys/fs/cgroup:ro"
OPTS+=" -e DOCKER_FIX=''"
#OPTS+=" -e OPENSEARCH_HOSTS=https://${ADDRESS['elk1']}:9200,https://${ADDRESS['elk2']}:9200,https://${ADDRESS['elk3']}:9200,https://${ADDRESS['elk4']}:9200"
OPTS+=" -e OPENSEARCH_HOSTS=https://localhost:9200"

# Run docker
echo "Starting docker container: $NAME"
# Start from a fresh container
docker run $OPTS $VOLUMES -h $NAME --name ${NAME} $IMAGE

echo "Done"
