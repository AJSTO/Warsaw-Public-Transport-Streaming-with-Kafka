# Warsaw-Public-Transport-Streaming-with-Kafka

## 👨‍💻 Built with
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" /> <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white"/> <img src="https://developers.redhat.com/sites/default/files/styles/article_feature/public/blog/2018/07/kafka-logo-wide.png?itok=_RFAAAS5" width="100" height="27,5" /> <img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white" /> <img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white" /><img src="https://www.devagroup.pl/blog/wp-content/uploads/2022/10/logo-Google-Looker-Studio.png" width="100" height="27,5" /><img src="https://www.scitylana.com/wp-content/uploads/2019/01/Hello-BigQuery.png" width="100" height="27,5" /> <img src="https://insightfinder.com/wp-content/uploads/Google-Cloud-Pub-sub.png" width="100" height="27,5" />

### ℹ️Project info

# [Warsaw Public Transport Dashboard](https://lookerstudio.google.com/reporting/97c14ac0-4f79-4041-921a-1742a978bfd4)

![Project Screenshot](/dashboard-v1.gif)

The **Warsaw Public Transport Dashboard** is an interactive data visualization project that streams real-time information about public transport buses and trams in Warsaw. It provides a live view of bus and tram locations, as well as detailed route information. This README serves as a guide to set up and run the project, whether you want to use Kafka for local development or leverage Google Pub/Sub for production deployment.

## Overview

The project gathers data from [https://api.um.warszawa.pl/](https://api.um.warszawa.pl/) to capture real-time information about the location of public transport buses and trams in Warsaw. It offers the following key features:

- Real-time tracking of bus and tram locations.
- Visualization of bus and tram routes.
- Interactive dashboard for exploring public transport data.

## Local Development with Kafka

If you want to run this project locally using Kafka for data streaming, follow the steps outlined in the [Local Development Setup](/local-setup.md) section. This section will guide you through the installation of necessary components, running Kafka, and configuring the project to consume data from the Kafka topic.

## Production Deployment with Google Pub/Sub

For production deployment or if you want to leverage the capabilities of Google Pub/Sub for data streaming, refer to the [Production Deployment Guide](/production-deployment.md). This guide will walk you through setting up a Google Cloud project, creating a Pub/Sub topic, and configuring your project to publish and consume data using Google Pub/Sub.

## Generating Tram and Bus Routes / Bus Stops

In addition to real-time tracking, this project also offers functionality to capture and draw tram and bus routes from the gathered data. To draw routes and get bus stops localisation explore [creating_routes_with_bus_stops](/creating_routes_with_bus_stops)

## Contributing

We welcome contributions and bug reports.

## License

This project is licensed under the [MIT License](/LICENSE).

---

Happy exploring the public transport data of Warsaw!
