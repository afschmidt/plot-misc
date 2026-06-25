# `docker` directory

Build files for the `floriaan1/plot-misc:master` image used in GitLab CI/CD.

The image is used **only** by the `pages` job to build the Sphinx
documentation: it bakes in the scientific stack plus Sphinx/pandoc so the docs
build is fast on Alpine/musl. 
Unit tests run on stock `python:*-slim` images, not this one.
This is **not** a distributable image of the package itself.

Build a fresh image:

```sh
./build.sh
```

Push to Docker Hub:

```sh
docker image list
sudo docker push docker.io/<USERNAME>/plot-misc:master
```

Remove the local image, or pull it from Docker Hub:

```sh
docker image prune -a
sudo docker pull floriaan1/plot-misc:master
```
