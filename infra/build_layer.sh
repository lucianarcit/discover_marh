#!/bin/bash
# Build Lambda Layer com dependências Python
# Uso: bash build_layer.sh

set -e

LAYER_DIR=".build/layer/python"
rm -rf .build/layer
mkdir -p "$LAYER_DIR"

pip install \
  --target "$LAYER_DIR" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  pydantic pydantic-core annotated-types typing-inspection

cd .build/layer
zip -r ../layer.zip .
echo "Layer criado em .build/layer.zip"
