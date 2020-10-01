#!/bin/bash
docker_name="csu-covid19-sign"
docker restart ${docker_name} && docker logs -f ${docker_name}