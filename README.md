# Kong API Gateway Integration

Kong API Gateway is a powerful and flexible open-source tool designed to manage, secure, and extend your APIs. By integrating Kong into your system, you can leverage its extensive capabilities to ensure smooth API traffic management, enhanced security, and simplified monitoring and logging. This guide will help you integrate Kong API Gateway with your existing infrastructure, ensuring a robust and efficient API management solution.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Adding Code in Your Yaml File](#adding-code-in-your-yaml-file)
4. [Configuration](#configuration)
5. [Adding Services and Routes](#adding-services-and-routes)
6. [Securing APIs](#securing-apis)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Scaling and Performance](#scaling-and-performance)
9. [Troubleshooting](#troubleshooting)
10. [Conclusion](#conclusion)
11. [References](#references)

## Introduction

Kong API Gateway acts as a middleware between your clients and your upstream services, providing features such as load balancing, rate limiting, and authentication. This integration will allow you to manage your API traffic efficiently, secure your endpoints, and monitor performance with ease.

## Prerequisites

Before you begin, ensure you have the following:

- Docker installed on your machine.
- Basic knowledge of API concepts and Docker.
- Access to your API services and routes.

## Adding Code in Your Yaml File

bash```
version: "3.1.0"

x-kong-config: &kong-env
  KONG_DATABASE: ${KONG_DATABASE:-postgres}
  KONG_PG_DATABASE: ${KONG_PG_DATABASE:-kong}
  KONG_PG_HOST: db
  KONG_PG_USER: ${KONG_PG_USER:-kong}
  KONG_PG_PASSWORD_FILE: /run/secrets/kong_postgres_password

services:
  ###############---API-1---###############
  api1:
    container_name: API-1
    build:
      context: ./01_service
      dockerfile: Dockerfile
    port:
      - 8001:8001
    volumes:
      - ./01_service:/app
 ###############---API-2---###############
    api2:
      container_name: API-2
      build:
        context: ./02_service
        dockerfile: Dockerfile
      port:
        - 8002:8002
      volumes:
        - ./02_service:/app
  ######################################------KONG-MIGRATION------#####################################################
  kong-migrations:
    image: "${KONG_DOCKER_TAG:-kong:latest}"
    command: kong migrations bootstrap
    profiles: ["database"]
    depends_on:
      - db
    environment:
      <<: *kong-env
    secrets:
      - kong_postgres_password
    restart: on-failure

  kong-migrations-up:
    image: "${KONG_DOCKER_TAG:-kong:latest}"
    command: kong migrations up && kong migrations finish
    profiles: ["database"]
    depends_on:
      - db
    environment:
      <<: *kong-env
    secrets:
      - kong_postgres_password
    restart: on-failure

  kong:
    image: "${KONG_DOCKER_TAG:-kong:latest}"
    user: "${KONG_USER:-kong}"
    environment:
      <<: *kong-env
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_PROXY_LISTEN: "${KONG_PROXY_LISTEN:-0.0.0.0:8000}"
      KONG_ADMIN_LISTEN: "${KONG_ADMIN_LISTEN:-0.0.0.0:8001}"
      KONG_ADMIN_GUI_LISTEN: "${KONG_ADMIN_GUI_LISTEN:-0.0.0.0:8002}"
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_PREFIX: ${KONG_PREFIX:-/var/run/kong}
      KONG_DECLARATIVE_CONFIG: "/opt/kong/kong.yaml"
    secrets:
      - kong_postgres_password
    ports:
      - "${KONG_INBOUND_PROXY_LISTEN:-0.0.0.0}:8000:8000/tcp"
      - "${KONG_INBOUND_SSL_PROXY_LISTEN:-0.0.0.0}:8443:8443/tcp"
      - "127.0.0.1:8001:8001/tcp"
      - "127.0.0.1:8444:8444/tcp"
      - "127.0.0.1:8002:8002/tcp"
    healthcheck:
      test: ["CMD", "kong", "health"]
      interval: 10s
      timeout: 10s
      retries: 10
    restart: on-failure:5
    read_only: true
    volumes:
      - kong_prefix_vol:${KONG_PREFIX:-/var/run/kong}
      - kong_tmp_vol:/tmp
    security_opt:
      - no-new-privileges
  db:
    image: postgres:latest
    profiles: ["database"]
    environment:
      POSTGRES_DB: ${KONG_PG_DATABASE:-kong}
      POSTGRES_USER: ${KONG_PG_USER:-kong}
      POSTGRES_PASSWORD_FILE: /run/secrets/kong_postgres_password
    secrets:
      - kong_postgres_password
    healthcheck:
      test:
        [
          "CMD",
          "pg_isready",
          "-d",
          "${KONG_PG_DATABASE:-kong}",
          "-U",
          "${KONG_PG_USER:-kong}",
        ]
      interval: 30s
      timeout: 30s
      retries: 3
    restart: on-failure
    stdin_open: true
    tty: true
    volumes:
      - kong_data:/var/lib/postgresql/data
####################################################------VOLUMES------#####################################################
volumes:
  kong_data: {}
  kong_prefix_vol:
    driver_opts:
      type: tmpfs
      device: tmpfs
  kong_tmp_vol:
    driver_opts:
      type: tmpfs
      device: tmpfs
##############################################------NETWORKS------################################################################
networks:
  kong-net:
    driver: bridge
############################################------SECRETS------###################################################################
secrets:
  kong_postgres_password:
    file: ./POSTGRES_PASSWORD

## Configuration

Configure Kong to manage your API services by updating the `kong.conf` file or using environment variables. Key configurations include database settings, cache configuration, and logging levels. 

## Adding Services and Routes

Kong uses Services and Routes to define API endpoints:
- Create script.sh file
- Then follow below instructions

1. **Add a Service**:
    ```sh
    curl -i -X POST http://localhost:8001/services/ \
        --data "name=example-service" \
        --data "url=http://example.com"
    ```

2. **Add a Route**:
    ```sh
    curl -i -X POST http://localhost:8001/services/example-service/routes \
        --data "paths[]=/example"
    ```

## Securing APIs

Secure your APIs by enabling plugins such as key-auth, rate-limiting, or JWT:

1. **Enable Key Authentication**:
    ```sh
    curl -i -X POST http://localhost:8001/services/example-service/plugins \
        --data "name=key-auth"
    ```

2. **Add a Consumer**:
    ```sh
    curl -i -X POST http://localhost:8001/consumers/ \
        --data "username=example_user"
    ```

3. **Create a Key for the Consumer**:
    ```sh
    curl -i -X POST http://localhost:8001/consumers/example_user/key-auth/ \
        --data "key=your-api-key"
    ```

## Monitoring and Logging

Utilize Kong's built-in logging and monitoring tools:

- **Enable Logging Plugins** (e.g., file-log, http-log):
    ```sh
    curl -i -X POST http://localhost:8001/services/example-service/plugins \
        --data "name=file-log" \
        --data "config.path=/var/log/kong/example.log"
    ```

- **Monitor API Performance** using tools like Grafana and Prometheus.

## Scaling and Performance

Kong can be scaled horizontally to handle increased traffic. Deploy Kong in a clustered environment and use a load balancer to distribute the traffic. Ensure database performance is optimized to handle the load.

## Troubleshooting

Common issues and their solutions:

- **Database Connection Issues**: Verify the database configuration and connectivity.
- **Plugin Errors**: Check plugin configurations and logs for detailed error messages.
- **API Gateway Performance**: Monitor system resources and optimize configurations accordingly.

## Conclusion

Integrating Kong API Gateway into your infrastructure enhances your API management capabilities, providing robust security, traffic control, and monitoring features. Follow this guide to set up and configure Kong, ensuring a scalable and efficient API management solution.

## References

- [Kong Official Documentation](https://docs.konghq.com/)
- [Kong Docker Hub](https://hub.docker.com/_/kong)
- [Kong Plugins](https://docs.konghq.com/hub/)

Feel free to contribute to this repository or raise issues if you encounter any problems during the integration process.
