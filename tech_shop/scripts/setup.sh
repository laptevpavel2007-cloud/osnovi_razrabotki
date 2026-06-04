#!/bin/sh
set -e

pip install -r requirements.txt

python -c "from packages.core.database import Database; Database().init_schema()"
