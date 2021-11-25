#!/usr/bin/env bash
set -eo pipefail

# Build and publish the specified version of the data_analysis Factorio tool to Docker Hub (also builds latest image)

REPO_USERNAME="dedlyspyder"
IMAGE_REPO_NAME="factorio-data-analysis"


if [[ -z "$1" ]]; then
  echo "Missing version to build"
  echo "Usage: $0 [version] (-l)"
  echo "  -l will not push changes to docker hub"
  exit 1
fi

VERSION="$1"
LOCAL=false
if [[ "$2" == "-l" ]]; then
  LOCAL=true
fi

HERE="$(readlink -f "$(dirname "$)")")"

echo "Building $VERSION and latest tags for $IMAGE_REPO_NAME"
docker build "$HERE" \
  -t "$IMAGE_REPO_NAME:$VERSION" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:$VERSION" \
  -t "$IMAGE_REPO_NAME:latest" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:latest"

if [ "$LOCAL" == false ]; then
  echo "Pushing $REPO_USERNAME/$IMAGE_REPO_NAME"
  docker push -a "$REPO_USERNAME/$IMAGE_REPO_NAME"

  mapfile -t images_to_cleanup < <(docker images "$REPO_USERNAME/$IMAGE_REPO_NAME" | grep "$REPO_USERNAME" | grep -Ev 'latest|<none>' | awk '{print $1":"$2}')
  for image in "${images_to_cleanup[@]}"; do
    docker rmi "$image"
  done
fi
