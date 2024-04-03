#!/usr/bin/env sh
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=2:ss=2:sts=2:sw=2:ft=sh

# Title:            build_db.sh
# Description:      Build Postgres DB
# Author:           Ricky Laney
# Version:          0.1.0
# ==============================================================================

CREATE DATABASE rsgolfdb;
CREATE USER rsgolfdb_owner WITH PASSWORD 'MYPASSWORD';
ALTER ROLE rsgolfdb_owner SET client_encoding TO 'utf8';
ALTER ROLE rsgolfdb_owner SET default_transaction_isolation TO 'read committed';
ALTER ROLE rsgolfdb_owner SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE rsgolfdb TO rsgolfdb_owner;
