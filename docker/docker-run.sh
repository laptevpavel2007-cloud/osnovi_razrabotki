#!/usr/bin/env bash
set -e

docker network create microservices-net 2>/dev/null || echo "Сеть уже существует"

docker run -d \
  --name db \
  --network microservices-net \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=app \
  -e POSTGRES_DB=orders \
  -p 5432:5432 \
  postgres:16


sleep 5

docker build -t product-service-img ./product_service

docker run -d \
  --name product-service \
  --network microservices-net \
  -p 8001:8000 \
  product-service-img

docker build -t discount-service-img ./discount_service

docker run -d \
  --name discount-service \
  --network microservices-net \
  -p 8003:8000 \
  discount-service-img

docker build -t order-service-img ./order_service

docker run -d \
  --name order-service \
  --network microservices-net \
  -p 8002:8000 \
  -e PRODUCT_SERVICE_URL=http://product-service:8000 \
  -e DISCOUNT_SERVICE_URL=http://discount-service:8000 \
  -e DATABASE_URL=postgresql://app:app@db:5432/orders \
  order-service-img