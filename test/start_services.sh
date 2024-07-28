#!/bin/bash

# Function to check if a Docker image exists
image_exists() {
  docker images | grep -q "$1"
}

# Function to check if a Docker container exists
container_exists() {
  docker ps -a | grep -q "$1"
}

# Pull Docker images
echo "Pulling Docker images..."

if ! image_exists "minio/minio"; then
  docker pull minio/minio >> docker_pull.log 2>&1
fi

if ! image_exists "emqx/emqx"; then
  docker pull emqx/emqx >> docker_pull.log 2>&1
fi

if ! image_exists "redis"; then
  docker pull redis >> docker_pull.log 2>&1
fi

if ! image_exists "nsqio/nsq"; then
  docker pull nsqio/nsq >> docker_pull.log 2>&1
fi

echo "Docker images pulled successfully."

# Start MinIO container
if ! container_exists "minio"; then
  echo "Starting MinIO..."
  nohup docker run -p 9000:9000 -p 9090:9090 --name minio -e "MINIO_ROOT_USER=admin" -e "MINIO_ROOT_PASSWORD=admin1234" -v /mydata/minio/data:/data -v /mydata/minio/config:/root/.minio -d minio/minio server /data --console-address ":9000" --address ":9090" > minio.log 2>&1 &
  echo "MinIO started."
else
  echo "MinIO container already exists, skipping..."
fi

# Start EMQX container
if ! container_exists "emqx"; then
  echo "Starting EMQX..."
  nohup docker run -d --name emqx --privileged=true -p 1883:1883 -p 8883:8883 -p 8083:8083 -p 8084:8084 -p 8081:8081 -p 18083:18083 emqx/emqx:latest > emqx.log 2>&1 &
  echo "EMQX started."
else
  echo "EMQX container already exists, skipping..."
fi

# Start Redis container
if ! container_exists "myredis"; then
  echo "Starting Redis..."
  nohup docker run --name myredis -it -p 6379:6379 -v /data/redis-data redis --requirepass "123456" > redis.log 2>&1 &
  echo "Redis started."
else
  echo "Redis container already exists, skipping..."
fi

# Start nsqlookupd container
if ! container_exists "nsqlookupd"; then
  echo "Starting nsqlookupd..."
  nohup docker run --name nsqlookupd -p 4160:4160 -p 4161:4161 nsqio/nsq /nsqlookupd > nsqlookupd.log 2>&1 &
  echo "nsqlookupd started."
else
  echo "nsqlookupd container already exists, skipping..."
fi

# Start nsqd container
if ! container_exists "nsqd"; then
  echo "Starting nsqd..."
  nohup docker run --name nsqd -p 4150:4150 -p 4151:4151 -d nsqio/nsq /nsqd --broadcast-address=172.17.0.1 --lookupd-tcp-address=172.17.0.1:4160 --data-path=/data > nsqd.log 2>&1 &
  echo "nsqd started."
else
  echo "nsqd container already exists, skipping..."
fi

# Start nsqadmin container
if ! container_exists "nsqadmin"; then
  echo "Starting nsqadmin..."
  nohup docker run -d --name nsqadmin -p 4171:4171 nsqio/nsq /nsqadmin --lookupd-http-address=172.17.0.1:4161 > nsqadmin.log 2>&1 &
  echo "nsqadmin started."
else
  echo "nsqadmin container already exists, skipping..."
fi

echo "All services started successfully."

