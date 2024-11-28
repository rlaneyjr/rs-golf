#!/bin/bash
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=2:ss=2:sts=2:sw=2:ft=bash

# Title:            startup.sh
# ==============================================================================

gunicorn --bind 0.0.0.0:8000 --log-file logging/gunicorn.log --workers 2 core.wsgi
