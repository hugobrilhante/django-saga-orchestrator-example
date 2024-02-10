#!/bin/bash

set -e

check_status() {
    status=$(curl -s -o /dev/null 2>&1 -w "%{http_code}" http://127.0.0.1:15672)

    if [ "$status" -eq 200 ]; then
        return 0
    else
        return 1
    fi
}

echo "Running migrations..."

source scripts/manage.sh order migrate 
source scripts/manage.sh stock migrate 
#source scripts/manage.sh payment migrate 

echo "Loading data..."

source scripts/manage.sh order loaddata order 
source scripts/manage.sh stock loaddata stock 
#source scripts/manage.sh payment loaddata payment 

# Starting RabbitMQ to create the exchange
docker compose up -d rabbitmq 

while ! check_status; do
    echo "Creating saga exchange..."
    sleep 10
done

docker compose exec rabbitmq rabbitmqadmin declare exchange name=saga type=topic 

# Stopping RabbitMQ
docker compose stop rabbitmq 

echo "Starting services..."

source scripts/run.sh up order stock  rabbitmq