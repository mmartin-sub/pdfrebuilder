#!/bin/bash
set -e

echo "Running linting checks..."
hatch run format-check
hatch run lint-check
hatch run types-pyright

echo "Running tests with coverage..."
hatch run test-cov
