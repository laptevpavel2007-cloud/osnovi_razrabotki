# Диагностика: намеренно сломанные конфигурации

Этот документ описывает типичные ошибки при работе с Docker Compose и микросервисной архитектурой. Каждая ошибка была воспроизведена намеренно, чтобы понять, почему она возникает и как её правильно исправить.

Docker Compose просто читает YAML-файл и переводит его в команды `docker run`. Любая ошибка в Compose — это ошибка в понимании того, как работают контейнеры, сети и порты.


## Ошибка 1: `127.0.0.1` вместо имени сервиса

### Сломанная конфигурация

В `docker-compose.yaml` для `order-service` указаны localhost-адреса:

```yaml
services:
  order-service:
    build: ./order_service
    environment:
      PRODUCT_SERVICE_URL: http://127.0.0.1:8001    
      DISCOUNT_SERVICE_URL: http://127.0.0.1:8003  
      DATABASE_URL: postgresql://app:app@127.0.0.1:5432/orders 