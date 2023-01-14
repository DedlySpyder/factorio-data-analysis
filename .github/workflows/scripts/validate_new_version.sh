#!/usr/bin/env bash
set -exo pipefail

REPO="dedlyspyder"
IMAGE="factorio-data-analysis"

if [[ -z "$1" ]]; then
  echo "::error Usage: $0 [factorio version]"
  exit 1
fi
image_tag="$1"

if curl -sSLf "https://hub.docker.com/v2/repositories/$REPO/$IMAGE/tags/$image_tag" > /dev/null; then
  echo "exists=true" >> $GITHUB_OUTPUT
else
  echo "exists=false" >> $GITHUB_OUTPUT
fi
