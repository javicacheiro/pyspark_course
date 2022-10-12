#!/bin/bash
#
# Script to start opensearch servers
#

NAME=$(hostname -s)

# Name of the docker image to use
VERSION="1.3.4"
IMAGE="opensearchproject/opensearch:$VERSION"

# Create empty data volume if needed
mkdir /data/opensearch
chown 1000:1000 /data/opensearch

# Generate storage options for the container
VOLUMES=" -v /data/opensearch:/data"

# Docker custom options
OPTS+=" -d "
OPTS+=" --restart=unless-stopped "
#OPTS+=" --privileged"
OPTS+=" --net=host"
#OPTS+=" -v /sys/fs/cgroup:/sys/fs/cgroup:ro"
OPTS+=" -e DOCKER_FIX=''"
OPTS+=" -e cluster.name=opensearch-cesga-dev"
OPTS+=" -e network.host=0.0.0.0"
OPTS+=" -e discovery.type=single-node"
OPTS+=" -e bootstrap.memory_lock=true"
OPTS+=" --ulimit memlock=-1:-1"
OPTS+=" --ulimit nofile=65536:65536"
OPTS+=" -e path.data=/data"

# The default heap size is only 1GB
# Don't allocate more than 32GB. Pointers blow up then because 4 bytes are no longer enough.
OPENSEARCH_JAVA_OPTS="-Xms1g -Xmx1g"

# Tuning
# The vm.max_map_count kernel setting must be set to at least 262144 for production use.
sysctl -w vm.max_map_count=262144

# Run docker
echo "Starting docker container: $NAME"
# Start from a fresh container
docker run $OPTS -e "OPENSEARCH_JAVA_OPTS=$OPENSEARCH_JAVA_OPTS" $VOLUMES -h $NAME --name ${NAME} $IMAGE
#docker run $OPTS $VOLUMES -h $NAME --name ${NAME} $IMAGE
# Restart a previous container
#echo "Reusing a previously stopped container: if this is not what you want edit the script"
#docker start ${NAME}

echo "Now remember to start kibana"
