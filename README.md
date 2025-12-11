
# Live SFMTA MUNI Map

## Overview
A fully automated 24/7 data pipeline processing **500,000+ vehicle records daily** to visualize San Francisco's public transit system in real-time.

**[Live Demo](https://polar3197.github.io/muni-frontend/)** | **[API](https://another-northern-epinions-wallpaper.trycloudflare.com/)**

<img width="1433" height="742" alt="Screenshot 2025-12-11 at 11 58 58 AM" src="https://github.com/user-attachments/assets/492ce689-cd11-4823-a479-33a82feb3ae4" />
I was inspired to see if I could map all public transportation vehicles in San Francisco in real-time. This project taught me about processing large volumes of data quickly and cost-effectively. Since then I have been adding simple but often overlooked mapping features.

## Features
- Real-time tracking of 500+ buses across 60+ routes, updated every 60 seconds (as constrained by GTFS rate limiter)
- Interactive route filtering with occupancy indicators (empty, few riders, several, many)
- Historical data access - query patterns across 1.7M+ records per week

## Tech Stack:
Python, FastAPI, PostgreSQL, Docker, AWS S3, JavaScript, CSS, HTML, Leaflet.js

## Architecture

<img width="938" height="466" alt="Screenshot 2025-12-11 at 11 59 46 AM" src="https://github.com/user-attachments/assets/02fcf6d8-ecfe-4ea7-9a0a-33d51a1ccac1" />

1. Fetch Protocol Buffer from GTFS, verify and trim data to JSON format of necessary fields
2. Store vehicle information in PostgreSQL database.
3. FastAPI endpoint runs continuously in Docker container, allowing frontend JavaScript to request current vehicle positions from the PostgreSQL database. The endpoint is made public via a cloudflared tunnnel.
4. Once per week, the oldest partition of the vehicles table (partitions contain a weeks worth of data ~1.7m vehicle snapshots) is exported into S3 bucket.

## Technical Highlights

  **PostgreSQL:**
    - Weekly partitions (~3.5M records each) for efficient time-series queries
    - Composite indexes on `(route_id, timestamp)` for optimized filtering
    - Automatic partition exporting reduces query scope to past four weeks only
    - Partition management automated via weekly cron job
  
  **S3 Tiered Storage:**
    - Day 0-28: PostgreSQL hot storage for fast queries
    - Day 28-118: Glacier Instant Retrieval (instant access, $0.004/GB/month)
    - Day 118+: Glacier Flexible Retrieval (3-5 hour retrieval, $0.0036/GB/month)
    - 95% storage cost reduction vs S3 Standard for long-term data
    - Automated lifecycle management with Parquet compression (80% size reduction)
  
  **FastAPI Backend:**
    - Asynchronous request handling for high concurrency
    - Async database queries with SQLAlchemy for non-blocking I/O
    - RESTful API serving 500+ vehicle positions with <100ms latency

## API Endpoints

- `GET /` - API documentation
- `GET /health` - Service health check
- `GET /vehicles/current` - Current positions of all active vehicles
- `GET /vehicles/{vehicle_id}` - Historical data for specific vehicle

**Example response:**
```json
{
  "vehicle_id": 1010,
  "route_id": "F",
  "lat": 37.762596,
  "lon": -122.434334,
  "timestamp": "2025-12-11T19:45:55Z"
}
```

## Future Enhancements
- **Outline route paths and show stops**
- **Address lag** caused by rendering 500+ vehicles on GitHub Pages site..
- **Spatial interpolation** of vehicle locations between alotted API polls. Exciting areas this explores: predictive/physics modeling, route-fitting, Kalman filtering.
- **Natural language interface**, for example "Show me all busses currently in Russian Hill". This would simplify the interface appearance by removing explicit buttons and instead allow a chat window with prompt suggestions. Exciting areas this explores: LLM integration, advanced RESTful API calls, agents with tools.
