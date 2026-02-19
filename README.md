# Drive to Iftar 🏎️🌙

Fast-paced, multiplayer racing game built for the modern web.

## 🚀 How It Works

**Drive to Iftar** is built on a highly optimized architecture designed to handle massive amounts of concurrent players with minimal server load.

### 🧠 The optimization: Seed-Based Procedural Generation

Instead of the server constantly streaming heavy map data (like road segments, obstacles, or building positions) to every player, the game uses **Deterministic Procedural Generation**.

1.  **The Seed**: When a game starts, the backend generates a single random "seed" (e.g., `race_123_seed_xyz`).
2.  **Client-Side Generation**: This seed is sent to all connected clients. Using a custom seeded Random Number Generator (RNG), every client generates the **exact same track, obstacles, and scenery locally**.
3.  **Massive Bandwidth Savings**: The only data traveling over the network is high-level player state (position, lane change, drift status). The server doesn't need to know *where* a building is, because every client already knows.

This allows the backend to handle thousands of concurrent connections on very modest hardware, as the heavy lifting of world generation is distributed to the clients.

## 🛠️ Technology Stack & Justification

I chose a cutting-edge stack specifically for performance, responsiveness, and developer experience.

### Frontend: SvelteKit + Threlte (Three.js)

*   **SvelteKit**: Unlike React or Vue, Svelte compiles away the framework, resulting in tiny bundle sizes and zero virtual DOM overhead. This is crucial for maintaining high FPS in a browser-based game.
*   **Threlte**: A Svelte wrapper for Three.js that provides a declarative way to build 3D scenes. It leverages Svelte's reactivity to update 3D objects efficiently without manual DOM manipulation or heavy re-renders.
*   **Performance**: The combination allows for "close to metal" WebGL performance while keeping the codebase clean and component-based.

### Backend: FastAPI + WebSockets

*   **Performance**: FastAPI is one of the fastest Python frameworks available, built on Starlette and Pydantic. It uses asynchronous programming (async/await) natively, making it perfect for handling thousands of concurrent WebSocket connections.
*   **Efficiency**: Python's async capabilities allow the server to manage game states, broadcasting, and database writes without blocking the main thread.
*   **Resource Usage**: Compared to heavier frameworks, FastAPI is lightweight and efficient, utilizing minimal CPU and RAM per connection.

### Why FastAPI over PHP (Laravel)?

While Laravel is a robust framework for traditional CRUD applications, I chose **FastAPI** for this multiplayer game for several key reasons:

1.  **Concurrency Model**: PHP's traditional synchronous execution model (one process per request) struggles with long-lived WebSocket connections required for real-time multiplayer gaming. FastAPI's `async/await` pattern allows a single process to handle thousands of concurrent connections efficiently.
2.  **Performance**: Python with FastAPI serves as a high-performance wrapper around Starlette and Pydantic, offering significantly lower latency and resource overhead compared to a full-stack PHP framework when managing rapid game state updates.
3.  **Unified Async Ecosystem**: By using **Alembic** for migrations and SQLAlchemy (Async) for database interactions, the entire backend operates non-blocking. This ensures that database writes (like saving high scores) never interrupt the game loop or cause lag for other players.

### ⚡ Performance Optimization: Non-Blocking Logger

To ensure zero latency spikes during intense gameplay, the backend utilizes a custom **Queue-Based Logging System**.

*   **The Problem**: Standard logging writes directly to `stdout` or files, which is a blocking I/O operation. If the disk is slow or under load, a simple `log.info()` could pause the entire game loop for milliseconds, causing jitter for players.
*   **The Solution**: I implemented a `QueueHandler` that instantly pushes log records to an in-memory queue and returns control immediately. A separate background thread (`QueueListener`) consumes this queue and handles the actual writing.
*   **The Result**: Logging becomes effectively "free" for the main game thread, ensuring consistent tick rates even under heavy load.

### Infrastructure: Docker & Nginx

*   **Dockerized**: The entire stack (Frontend, Backend, DB) is containerized for consistent deployment across any environment.
*   **Nginx Reverse Proxy**: Efficiently routes traffic, handles SSL termination, and manages WebSocket upgrades, offloading connection management from the application servers.

## 📦 Deployment

The project includes a `docker-compose.yml` for instant deployment.

1.  **Configure Environment**:
    ```bash
    cp .env.template .env
    # Edit .env with your credentials
    ```

2.  **Run with Docker**:
    ```bash
    docker compose up --build -d
    ```

The game will be available at `http://localhost:8001` (or your configured port).
