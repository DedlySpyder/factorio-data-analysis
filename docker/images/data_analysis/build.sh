#!/usr/bin/env bash
set -eou pipefail

# Build and publish the specified version of the data_analysis Factorio tool to Docker Hub (also builds latest image)

REPO_USERNAME="dedlyspyder"
IMAGE_REPO_NAME="factorio-data-analysis"


if [[ -z "$1" ]]; then
  echo "Missing version to build"
  echo "Usage: $0 [version]"
  exit 1
fi

VERSION="$1"

HERE="$(readlink -f "$(dirname "$)")")"

echo "Building $VERSION and latest tags for $IMAGE_REPO_NAME"
docker build "$HERE" \
  -t "$IMAGE_REPO_NAME:$VERSION" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:$VERSION" \
  -t "$IMAGE_REPO_NAME:latest" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:latest"

echo "Pushing $REPO_USERNAME/$IMAGE_REPO_NAME"
docker push -a "$REPO_USERNAME/$IMAGE_REPO_NAME"
