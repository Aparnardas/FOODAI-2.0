#!/usr/bin/env bash
set -e
cd ~/FoodAI2.0
zip -r FoodAI2.0_package.zip \
  app.py utils templates static data model requirements.txt run.sh \
  -x "static/uploads/*" "logs/*" "__pycache__/*" "*.pyc"
echo "✅ Packed: FoodAI2.0_package.zip"

