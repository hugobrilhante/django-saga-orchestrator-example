#!/bin/bash


set -eo pipefail

# Copy the .env.example file to .env
rename_env_files() {
    shopt -s dotglob
    for file in "$1"/*; do
        if [[ -d "$file" ]]; then
            rename_env_files "$file"
        elif [[ -f "$file" && "$file" == *.env.example ]]; then
            new_name="${file%.example}"
            new_name="${new_name}"
            cp "$file" "$new_name"
            echo "Copy: $file -> $new_name"
        fi
    done
}

# Services directory
services_dir="services"

# Copy rename the files
rename_env_files "$services_dir"

# Start necessary services
source ./scripts/services.sh start

# Run the web server in development
echo "Starting web server..."
npm --prefix ./web run dev
