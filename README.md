Overview (2-3 sentences + live demo link + screenshot)
This fully automated 24/7 data pipeline to fetch, store and visualize live SFMTA MUNI vehicle data. This project taught me about processing large volumes of data quickly and cost effectively. I am a public transit enthusiast. I spent time to make the infrastructure of this project solid and scaleable so that it can be built on and improved indefinitely. 

I was inspired, as a Bay Area resident, to see if I could map, in real-time, the locations of all public transportation vehicles in San Francisco. Since then I have been adding simple but often overlooked features, like showing the path of a bus route 
<img width="1433" height="742" alt="Screenshot 2025-12-11 at 11 58 58 AM" src="https://github.com/user-attachments/assets/492ce689-cd11-4823-a479-33a82feb3ae4" />

Features (bullet list of what it does)
- displays map of San Francisco with locations of all running public transit vehicles, updated every 60 seconds (as constrained by GTFS API rate limiter)

Tech Stack: Python, FastAPI, PostgreSQL, Docker, AWS S3, JavaScript, CSS, HTML, Leaflet.js


Architecture (diagram + brief explanation of data flow)
<img width="938" height="466" alt="Screenshot 2025-12-11 at 11 59 46 AM" src="https://github.com/user-attachments/assets/02fcf6d8-ecfe-4ea7-9a0a-33d51a1ccac1" />

Technical Highlights (partitioning strategy, Docker orchestration, S3 archival)
  PostgreSQL Partitioning Strategy:
    - index on timestamp and route for speed up in querying database for 
    - partitioning on weekAPI call to fetch current vehicles must be fast, 
  S3 Tiered Storage Strategy:
    -
  Docker Orchestration:
Performance (scale metrics: 600k records/day, query times, etc.)
Setup/Installation (how to run locally)
API Endpoints (brief documentation)

Future Enhancements (LLM integration, marker clustering, etc.)
- Spatial interpolation of vehicle locations between alotted API polls. Exciting areas this explores: predictive/physics modeling, route-fitting, Kalman filtering.
- Natural language interface, for example "Show me all busses currently in Russian Hill". This would simplify the interface appearance by removing explicit buttons and instead allow a chat window with prompt suggestions. Exciting areas this explores: LLM integration, advanced RESTful API calls, agents with tools.
- 
