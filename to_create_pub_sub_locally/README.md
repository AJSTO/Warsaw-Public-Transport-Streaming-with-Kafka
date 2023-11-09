# Kafka Basics:
## Topics:
* Kafka organizes messages into topics. Producers send messages to topics, and consumers subscribe to topics to receive those messages.
## Brokers:
* Kafka is designed to be distributed, and it relies on one or more Kafka brokers. Each broker is a server that stores the data and serves client requests.
## Zookeeper:
* Zookeeper is a distributed coordination service used by Kafka for managing and coordinating brokers. It helps maintain configuration information, naming, synchronization, and group services.
# Local Setup using Docker Compose:
## Zookeeper Container:
* The zookeeper service in your Docker Compose file provides a Zookeeper instance. Zookeeper is used by Kafka for coordination.
## Kafka Container:
* The kafka service provides a Kafka broker. It exposes Kafka on localhost:9092, and the KAFKA_ZOOKEEPER_CONNECT environment variable points to the Zookeeper instance.

## 1. Install Docker Compose:
Ensure that Docker Compose is installed on your machine. You can download it from the [official Docker Compose website](https://docs.docker.com/compose/install/).
## 2. Create a Project Directory:
Create a new directory for your Kafka project, and navigate to it in the terminal.
## 3. Create Docker Compose File:
Copy and paste your 'docker-compose.yaml' content into a file named 'docker-compose.yaml' in your project directory.
## 4. Start Docker Containers:
Open a terminal in your project directory and run the following command to start the Kafka and Zookeeper containers:
```bash
docker-compose up
```
This command will download the required images and start the containers.
## 5. Access Kafka:
Once the containers are up and running, Kafka should be accessible on 'localhost:9092'. This is the default Kafka broker address.
## 6. Testing with Kafka:
You can use the Kafka command-line tools or a Kafka client library in your preferred programming language to produce and consume messages. For example, you can use the kafka-console-producer and kafka-console-consumer tools.
To produce a test message:
```bash
docker exec -it kafka /opt/kafka_2.13-2.8.0/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
```
To consume messages from the "test" topic:
```bash
docker exec -it kafka /opt/kafka_2.13-2.8.0/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
```
Make sure to replace 'test' with your desired topic name.
## 7. Stop Containers:
When you're done working with Kafka, you can stop the containers with:
```bash
docker-compose down
```
This guide assumes that you have Docker Compose and Docker installed on your machine. Adjustments may be needed based on your specific requirements and environment.
