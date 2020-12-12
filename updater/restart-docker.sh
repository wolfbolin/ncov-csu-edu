#!/bin/bash
docker_name="risk-area-update"
docker restart ${docker_name} && docker logs -f ${docker_name}