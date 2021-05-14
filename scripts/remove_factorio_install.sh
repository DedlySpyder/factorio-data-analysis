#!/bin/bash

find ../factorio -mindepth 1 -maxdepth 1 -not -name mods -exec rm -rf "{}" \;

