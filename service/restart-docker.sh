#!/bin/bash
docker_name="csu-service"
docker restart ${docker_name} && docker logs -f ${docker_name}