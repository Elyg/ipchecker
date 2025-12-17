# ipchecker
docker for changing ip automatically for cloudflare

# dev and publish process

on docker extension
connect registry
select dockerhub
enter dockder id
enter password

In vscode:

Dockerfile
right click
build image

---

using the docker cli

docker login
docker build . -t ipchecker:dev
docker images
docker tag ipchecker:dev elyg/ipchekcer:dev
docker push elyg/ipchecker:dev