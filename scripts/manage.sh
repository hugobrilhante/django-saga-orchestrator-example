#!/bin/bash

# Script Name: manage.sh
# Description: Run Django management commands in a Docker container.
#
# Usage:
#  ./manage.sh <service_name> <django_command> [additional_arguments]
#
# Parameters:
#  - <service_name>:   Name of the Docker service/container where Django is running.
#  - <django_command>:  Django management command to be executed.
#  - [additional_arguments]:  Additional arguments to be passed to the Django management command.
#
# Examples:
#  ./manage.sh web migrate                 # Run Django's migrate command in the 'web' service.
#  ./manage.sh worker process_tasks --all   # Run a custom Django management command in the 'worker' service with additional arguments.
#
# Note:
#  - This script assumes that Docker Compose is installed on the system.
#  - Ensure proper permissions to execute this script.
#  - Make sure to specify the correct service name and Django management command.
#  - Additional arguments are optional and can be used to pass arguments to the Django management command.

# Extract arguments
SERVICE_NAME=$1
DJANGO_COMMAND=$2

# Run the Django management command in the specified Docker service
docker compose run --rm "$SERVICE_NAME" python manage.py "$DJANGO_COMMAND" "${@:3}"
