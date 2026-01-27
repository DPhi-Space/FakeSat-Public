# Satellite Simulation Dashboard

This project is a Django backend with a React + CesiumJS front-end that acts
as a dashboard for a real-time satellite simulation.

The external simulator is responsible for running the actual orbital
propagation and calls the REST API here roughly once per second to:

- POST satellite ground positions and timestamps
- GET the latest simulation control commands (start/stop/pause, step size, replay speed)

## Backend (Django)

### Setup

```bash
cd /home/user/DPHI/FakeSat-Public/src/dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Key models

- `Satellite`: basic satellite metadata.
- `Telemetry`: timestamped latitude/longitude (and optional altitude) samples.
- `SimulationControlState`: singleton-style record with the latest command.

### REST API

- `POST /api/telemetry/`

  ```json
  {
    "satellite": "SAT-1",
    "timestamp": "2026-01-27T12:00:00Z",
    "latitude": 40.0,
    "longitude": -75.0,
    "altitude": 500.0,
    "extra": {
      "any_future_field": "value"
    }
  }
  ```

- `GET /api/telemetry/recent/`

  Returns the most recent telemetry point for each active satellite:

  ```json
  {
    "telemetry": [
      {
        "satellite": "SAT-1",
        "timestamp": "2026-01-27T12:00:00Z",
        "latitude": 40.0,
        "longitude": -75.0,
        "altitude": 500.0,
        "extra": null
      }
    ]
  }
  ```

- `GET /api/commands/`

  ```json
  {
    "status": "running",
    "start_time": "2026-01-27T12:00:00Z",
    "step_size_seconds": 1,
    "replay_speed": 1.0
  }
  ```

- `POST /api/commands/`

  Partial updates to the command state; all fields optional:

  ```json
  {
    "status": "running",
    "start_time": "2026-01-27T12:00:00Z",
    "step_size_seconds": 1,
    "replay_speed": 1.0
  }
  ```

## Front-end (React + Vite + CesiumJS)

### Setup

```bash
cd frontend
npm install
npm run build
```

This builds into `frontend/dist`, which Django serves as static files.

### UI

- Cesium-based 3D globe showing the current satellite positions.
- Telemetry panel with current latitude, longitude, altitude and time.
- Simulation controls:
  - Set start time (ISO-8601 UTC)
  - Step size (seconds)
  - Replay speed (multiplier)
  - Start / Pause / Stop buttons.

The React app polls:

- `/api/telemetry/recent/` once per second for latest positions.
- `/api/commands/` once per second to stay in sync with the simulator.

