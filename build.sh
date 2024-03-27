#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=2:ss=2:sts=2:sw=2:ft=sh

# Title:            build.sh
# Description:      Render Build File
# Author:           Ricky Laney
# ==============================================================================

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
# python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
