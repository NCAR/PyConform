#!/bin/bash

set -e
set -eo pipefail

coverage run -m pytest tests/
coverage xml
