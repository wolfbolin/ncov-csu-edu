#!/bin/bash
docker_name="csu-signer"
docker restart ${docker_name} && docker logs -f ${docker_name}