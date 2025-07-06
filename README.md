# User Feed Microservice

## Project Overview

This project is a backend service responsible for managing and delivering personalized user feeds. It features an event-driven architecture where new publications are processed asynchronously to update the feeds of relevant followers. User feeds are stored in Redis for fast access and are retrievable via a secure API endpoint. The service is designed to be containerized using Docker and includes CI/CD workflows for automated builds and deployment.

## Folder Structure

The project is organized as follows:

```
.
├── .github/                    # GitHub specific files (e.g., Actions workflows)
│   └── workflows/
│       ├── docker-publish.yml  # Docker publishing workflow (e.g., for production)
│       └── docker-publish_qa.yml # Docker publishing workflow (e.g., for QA)
├── conections/                 # Modules for database and service connections
│   ├── mongo.py                # MongoDB connection utility
│   └── redis.py                # Redis connection utility
├── services/                   # Core business logic and service functions
│   └── functions.py            # Functions for feed processing and event consumption
├── .gitignore                  # Specifies intentionally untracked files for Git
├── dockerfile                  # Instructions to build the Docker image
├── main.py                     # Main application entry point (Flask API)
├── requirements.txt            # Python project dependencies
└── test.py                     # (Presumably) Automated tests for the application
```

**Key Directories & Files:**

*   **`conections/`**: Manages connections to external data stores like MongoDB and Redis.
*   **`services/`**: Contains the primary application logic, including processing incoming publication events and constructing user feeds.
*   **`main.py`**: Initializes and runs the Flask web server, exposing the API endpoints. It also starts the background event consumer.
*   **`dockerfile`**: Defines the environment and steps to build the application's Docker image.
*   **`.github/workflows/`**: Contains GitHub Actions configurations for CI/CD, automating the building and publishing of Docker images.

## Backend Design Pattern

The service primarily employs an **Event-Driven Architecture (EDA)**.
*   **Event Ingestion:** It listens to a Redis Stream (`stream_user_publications`) for new publication events. These events are likely published by another service or part of the system.
*   **Asynchronous Processing:** A background consumer thread processes these events asynchronously. When a new publication event is received, the service updates the feeds for all relevant followers.
*   **Decoupling:** This pattern decouples the publication creation process from the feed update process, enhancing scalability and resilience.

## Communication Architecture

The system utilizes several communication mechanisms:

1.  **Redis Streams (Message Broker):**
    *   Acts as the central event bus for new publications.
    *   The `stream_user_publications` stream is used to send publication data from producers to the feed service consumers.
    *   The service polls this stream to receive new events.

2.  **Redis Lists (Data Store/Cache for Feeds):**
    *   User-specific feeds are stored as lists in Redis (e.g., `feed:{user_id}`).
    *   This allows for quick writes (pre-calculating feeds) and fast reads when users request their feed.
    *   Feeds are trimmed to maintain a fixed size (e.g., latest 100 items).

3.  **HTTP/REST API (Flask):**
    *   A Flask application exposes a RESTful API for clients (e.g., frontend applications) to interact with the service.
    *   Currently, this is used for retrieving user feeds.
    *   Communication is synchronous (request-response).

4.  **Internal Threading:**
    *   Python's `threading` module is used to run the Redis stream consumer in a background thread, separate from the main Flask application thread. This ensures the API remains responsive while events are processed.

**Data Flow for New Publications:**
1. An external system publishes a message to the `stream_user_publications` Redis stream. This message includes publication details and follower information.
2. The background consumer in this service reads the message from the stream.
3. For each follower, the publication is added to their respective feed list in Redis.

## Folder Pattern

The project follows a **Responsibility-based Grouping** for its top-level directories:
*   **`conections/`**: Groups modules by their technical responsibility of managing database/service connections.
*   **`services/`**: Houses the core application logic and business features related to feed management.
*   Configuration files (`dockerfile`, `requirements.txt`), the main application entry point (`main.py`), and repository-specific configurations (`.github/`) are located appropriately at the root or in standard dedicated directories.

## API Endpoints

### Get User Feed

Retrieves the personalized feed for an authenticated user. Publications older than 24 hours are filtered out, and only unique publications are returned.

*   **Endpoint:** `/feed`
*   **Method:** `GET`
*   **Authentication:** Required (JWT Bearer Token)

**Request:**

*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
        *   The JWT token must contain a `user_id` in its payload.
*   **Body:** None

**Responses:**

*   **`200 OK` - Successful Response**
    *   **Content-Type:** `application/json`
    *   **Body Example:**
        ```json
        {
          "feed": [
            {
              "user_id": "publisher_user_123",
              "publication_id": "pub_abc789",
              "text": "Hello world!",
              "image_base64": null,
              "content_type": null,
              "datepublish": "2023-10-27T10:30:00"
            }
            // ... other publication objects
          ]
        }
        ```

*   **`401 Unauthorized` - Authentication Error**
    *   **Content-Type:** `application/json`
    *   **Body Examples:**
        *   `{"error": "Token missing or invalid"}`
        *   `{"error": "Invalid token payload"}`
        *   `{"error": "Token expired"}`
        *   `{"error": "Invalid token"}`
