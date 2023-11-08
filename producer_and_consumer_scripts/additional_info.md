### If you want to simplify you can create one docker-compose file for all containers in project:

### docker-compose.yaml:
```bash
version: '3.8'

services:
  zookeeper:
    build:
      context: .
      dockerfile: Dockerfile.kafka
    ports:
      - "2181:2181"

  kafka:
    build:
      context: .
      dockerfile: Dockerfile.kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_LISTENERS: INSIDE://kafka:9093,OUTSIDE://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_LISTENERS: INSIDE://0.0.0.0:9093,OUTSIDE://0.0.0.0:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  consumer_buses:
    build:
      context: .
      dockerfile: Dockerfile.consumer_buses_localisation
    depends_on:
      - kafka

  consumer_trams:
    build:
      context: .
      dockerfile: Dockerfile.consumer_trams_localiation
    depends_on:
      - kafka

  producer:
    build:
      context: .
      dockerfile: Dockerfile.producer
    depends_on:
      - kafka
```
### Dockerfile.kafka:
```bash
# Dockerfile for Kafka setup
FROM wurstmeister/zookeeper:latest
EXPOSE 2181

FROM wurstmeister/kafka:2.12-2.7.0
EXPOSE 9092
```

Don't forget to prepare config.yaml file:
```bash
api_key: YOUR-API-KEY-TO-API-UM-WARSAW
resource_id: YOUR-RESOURCE-ID-TO-API-UM-WARSAW
buses_topic: YOUR-KAFKA-TOPIC-1
trams_topic: YOUR-KAFKA-TOPIC-2
project_id: BIGQUERY-PROJECT-ID
dataset_id: DATASET-ID
bus_cords_table: TABLE-OF-BUSES-COORDINATES
tram_cords_table: TABLE-OF-TRAMS-COORDINATES
json_key_path: ./credentials.json
kafka_config:
  bootstrap_servers: localhost:9092
  group_id: mygroup
  auto_offset_reset: latest
```
And replace credentials.json on your Google Cloud json key.