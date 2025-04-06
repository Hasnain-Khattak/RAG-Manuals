#!/bin/bash
set -e

# Replace environment variables in nginx configuration
envsubst '${DOMAIN_NAME}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the main container command
exec "$@"