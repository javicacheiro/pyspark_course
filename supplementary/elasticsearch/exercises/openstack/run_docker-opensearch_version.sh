#!/bin/bash
#
# Script to start opensearch servers
#

NAME=$(hostname -s)

# Name of the docker image to use
VERSION="1.3.4"
IMAGE="opensearchproject/opensearch:$VERSION"

# Mappings
declare -A ADDRESS
ADDRESS["opensearch-1"]="10.38.28.237"
ADDRESS["opensearch-2"]="10.38.27.170"
ADDRESS["opensearch-3"]="10.38.28.8"
ADDRESS["kibana"]="10.38.29.17"

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
OPTS+=" --add-host=opensearch-1:${ADDRESS['opensearch-1']}"
OPTS+=" --add-host=opensearch-2:${ADDRESS['opensearch-2']}"
OPTS+=" --add-host=opensearch-3:${ADDRESS['opensearch-3']}"
OPTS+=" --add-host=kibana:${ADDRESS['kibana']}"
OPTS+=" -e DOCKER_FIX=''"
OPTS+=" -e cluster.name=opensearch-cesga-dev"
OPTS+=" -e node.name=$NAME"
OPTS+=" -e network.host=0.0.0.0"
OPTS+=" -e discovery.seed_hosts=opensearch-1,opensearch-2,opensearch-3"
OPTS+=" -e cluster.initial_master_nodes=opensearch-1,opensearch-2,opensearch-3"
OPTS+=" -e bootstrap.memory_lock=true"
OPTS+=" --ulimit memlock=-1:-1"
OPTS+=" --ulimit nofile=65536:65536"
OPTS+=" -e path.data=/data"

# The default heap size is only 1GB
# Don't allocate more than 32GB. Pointers blow up then because 4 bytes are no longer enough.
OPENSEARCH_JAVA_OPTS="-Xms8g -Xmx8g"

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

echo "Remember to start kibana in kibana vm"
