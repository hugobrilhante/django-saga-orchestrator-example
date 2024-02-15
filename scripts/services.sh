#!/bin/bash

set -e

# Function to run migrations
run_tests() {
    echo "Running migrations..."
    source scripts/manage.sh order test
    source scripts/manage.sh stock test
    source scripts/manage.sh payment test
}

# Function to run migrations
run_migrations() {
    echo "Running migrations..."
    source scripts/manage.sh order migrate > /dev/null 2>&1
    source scripts/manage.sh stock migrate > /dev/null 2>&1
    source scripts/manage.sh payment migrate > /dev/null 2>&1
}

# Function to load data
load_data() {
    echo "Loading data..."
    source scripts/manage.sh order loaddata order > /dev/null 2>&1
    source scripts/manage.sh stock loaddata stock > /dev/null 2>&1
    source scripts/manage.sh payment loaddata payment > /dev/null 2>&1
}

# Function to start RabbitMQ
start_rabbitmq() {
    echo "Starting RabbitMQ..."
    docker compose up -d rabbitmq  > /dev/null 2>&1
}

# Function to create exchange
create_exchange() {
    while ! check_status; do
        echo "Creating saga exchange..."
        sleep 10
    done
    docker compose exec rabbitmq rabbitmqadmin declare exchange name=saga type=topic > /dev/null 2>&1

}

# Function to start services
start_services() {
    echo "Starting services..."
    source scripts/run.sh up order stock payment rabbitmq> /dev/null 2>&1
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    source scripts/run.sh down order stock payment rabbitmq > /dev/null 2>&1
    docker volume prune -f > /dev/null 2>&1
}

# Function to check RabbitMQ status
check_status() {
    status=$(curl -s -o /dev/null 2>&1 -w "%{http_code}" http://127.0.0.1:15672)
    if [ "$status" -eq 200 ]; then
        return 0
    else
        return 1
    fi
}

# Function to run all parts
run_all() {
    run_migrations
    load_data
    start_rabbitmq
    create_exchange
    start_services
}

# Usage instructions
usage() {
    echo "Usage: $0 {tests|migrations|data|rabbitmq|exchange|services|stop|start}"
    echo "  tests: Run tests for order, stock, and payment"
    echo "  migrations: Run database migrations for order, stock, and payment"
    echo "  data: Load data into the database for order, stock, and payment"
    echo "  rabbitmq: Start RabbitMQ service"
    echo "  exchange: Create a RabbitMQ exchange for saga communication"
    echo "  services: Start order, stock, payment, and RabbitMQ services"
    echo "  start: Run all of the above steps"
    echo "  stop: Stop all running services"
    exit 1
}

# Choose which part to execute based on command line argument
case "$1" in
    tests)
        run_tests
        ;;
    migrations)
        run_migrations
        ;;
    data)
        load_data
        ;;
    rabbitmq)
        start_rabbitmq
        ;;
    exchange)
        create_exchange
        ;;
    services)
        start_services
        ;;
    stop)
        stop_services
        ;;
    start)
        run_all
        ;;
    *)
        usage
        ;;
esac
