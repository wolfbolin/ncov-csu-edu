#!/bin/bash
docker_name="risk-area-update"
docker image prune -f
docker stop ${docker_name}
docker rm ${docker_name}
echo -e "\033[5;36mOrz 旧容器(镜像)已清理\033[0m"

time_now=$(date "+%m%d%H")
docker build -f Dockerfile --tag ${docker_name}:"${time_now}" .
echo -e "\033[5;36mOrz 镜像重建完成\033[0m"

docker run -itd \
	--restart unless-stopped \
	--name ${docker_name} \
	--log-opt max-size=5m \
	-v $(pwd):/usr/local/app \
	${docker_name}:"${time_now}"
echo -e "\033[5;36mOrz 镜像启动完成\033[0m"
docker ps -a
docker logs ${docker_name} -f

