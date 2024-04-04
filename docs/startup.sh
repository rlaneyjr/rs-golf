#!/bin/bash
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=2:ss=2:sts=2:sw=2:ft=bash

# Title:            startup.sh
# ==============================================================================

python3 manage.py collectstatic && gunicorn --workers 2 core.wsgi --log-file -
