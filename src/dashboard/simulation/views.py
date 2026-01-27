from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from .models import Satellite, Telemetry, SimulationCommand


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


@csrf_exempt
def telemetry_ingest(request: HttpRequest) -> JsonResponse:
    """
    POST /api/telemetry/

    Expected JSON:
    {
      "satellite": "SAT-1",        # name or identifier
      "timestamp": "ISO-8601 UTC",
      "latitude": float,
      "longitude": float,
      "altitude": float?,          # km
      "extra": {...}?              # optional telemetry payload
    }
    """

    if request.method != "POST":
        return _json_error("Method not allowed", status=405)

    try:
        payload: dict[str, Any] = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return _json_error("Invalid JSON payload")

    sat_name = payload.get("satellite")
    if not sat_name:
        return _json_error("Missing 'satellite' field")

    timestamp_str = payload.get("timestamp")
    if not timestamp_str:
        return _json_error("Missing 'timestamp' field")

    timestamp: datetime | None = parse_datetime(timestamp_str)
    if timestamp is None:
        return _json_error("Invalid 'timestamp' format, expected ISO-8601")

    try:
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
    except (KeyError, TypeError, ValueError):
        return _json_error("Invalid or missing 'latitude'/'longitude'")

    altitude = payload.get("altitude")
    try:
        altitude_val = float(altitude) if altitude is not None else None
    except (TypeError, ValueError):
        return _json_error("Invalid 'altitude'")

    satellite, _ = Satellite.objects.get_or_create(name=sat_name)

    # Update or create the latest telemetry record for this satellite
    # This ensures we only store the most recently pushed position
    telemetry, created = Telemetry.objects.update_or_create(
        satellite=satellite,
        defaults={
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude_val,
            "extra": payload.get("extra") or None,
        },
    )

    return JsonResponse(
        {
            "id": telemetry.satellite_id,  # Use satellite_id as the primary key
            "satellite": satellite.name,
            "timestamp": telemetry.timestamp.isoformat(),
            "updated_at": telemetry.updated_at.isoformat(),
        },
        status=201 if created else 200,
    )


def telemetry_recent(request: HttpRequest) -> JsonResponse:
    """
    GET /api/telemetry/recent/

    Returns the latest telemetry for each active satellite (most recently pushed, by updated_at).
    """

    if request.method != "GET":
        return _json_error("Method not allowed", status=405)

    latest_points: list[dict[str, Any]] = []
    satellites = Satellite.objects.filter(active=True).select_related("latest_telemetry")
    
    for sat in satellites:
        # Use OneToOne relationship - each satellite has exactly one latest_telemetry record
        # Check if telemetry exists using hasattr or try/except
        if hasattr(sat, "latest_telemetry"):
            latest = sat.latest_telemetry
            latest_points.append(
                {
                    "satellite": sat.name,
                    "timestamp": latest.timestamp.isoformat(),
                    "latitude": latest.latitude,
                    "longitude": latest.longitude,
                    "altitude": latest.altitude,
                    "extra": latest.extra,
                }
            )

    return JsonResponse({"telemetry": latest_points})


@csrf_exempt
def commands(request: HttpRequest) -> JsonResponse:
    """
    GET /api/commands/  -> simulator polls to fetch all unconsumed commands (in order)
    POST /api/commands/ -> dashboard adds a command to the queue
    """

    if request.method == "GET":
        # Return all unconsumed commands in order, then mark them as consumed
        unconsumed = SimulationCommand.objects.filter(consumed=False).order_by("created_at")
        commands_list = [cmd.to_dict() for cmd in unconsumed]
        
        # Mark commands as consumed
        unconsumed.update(consumed=True)
        
        return JsonResponse({"commands": commands_list})

    if request.method != "POST":
        return _json_error("Method not allowed", status=405)

    try:
        payload: dict[str, Any] = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return _json_error("Invalid JSON payload")

    command_type = payload.get("command")
    if not command_type:
        return _json_error("Missing 'command' field")

    # Validate command type
    allowed_commands = {cmd[0] for cmd in SimulationCommand.COMMAND_TYPES}
    if command_type not in allowed_commands:
        return _json_error(f"Invalid command '{command_type}'", status=400)

    # Extract and validate parameters based on command type
    parameters: dict[str, Any] = {}
    
    if command_type == "set_start_time":
        start_time_str = payload.get("start_time")
        if start_time_str:
            dt = parse_datetime(start_time_str)
            if dt is None:
                return _json_error("Invalid 'start_time', expected ISO-8601", status=400)
            parameters["start_time"] = dt.isoformat()
    
    elif command_type == "set_step_size":
        if "step_size_seconds" in payload:
            try:
                val = int(payload["step_size_seconds"])
                if val <= 0:
                    raise ValueError
                parameters["step_size_seconds"] = val
            except (TypeError, ValueError):
                return _json_error("'step_size_seconds' must be a positive integer", status=400)
    
    elif command_type == "set_replay_speed":
        if "replay_speed" in payload:
            try:
                val_f = float(payload["replay_speed"])
                if val_f <= 0:
                    raise ValueError
                parameters["replay_speed"] = val_f
            except (TypeError, ValueError):
                return _json_error("'replay_speed' must be a positive number", status=400)
    
    # For start/pause/stop, parameters can include start_time, step_size, replay_speed
    # if they were provided (for convenience, so user can set params and start in one command)
    if command_type in ("start", "pause", "stop"):
        if "start_time" in payload:
            dt = parse_datetime(payload["start_time"])
            if dt is None:
                return _json_error("Invalid 'start_time', expected ISO-8601", status=400)
            parameters["start_time"] = dt.isoformat()
        
        if "step_size_seconds" in payload:
            try:
                val = int(payload["step_size_seconds"])
                if val <= 0:
                    raise ValueError
                parameters["step_size_seconds"] = val
            except (TypeError, ValueError):
                return _json_error("'step_size_seconds' must be a positive integer", status=400)
        
        if "replay_speed" in payload:
            try:
                val_f = float(payload["replay_speed"])
                if val_f <= 0:
                    raise ValueError
                parameters["replay_speed"] = val_f
            except (TypeError, ValueError):
                return _json_error("'replay_speed' must be a positive number", status=400)

    # Create the command
    cmd = SimulationCommand.objects.create(
        command_type=command_type,
        parameters=parameters,
    )

    return JsonResponse(
        {
            "id": cmd.id,
            "command": cmd.command_type,
            "parameters": cmd.parameters,
            "created_at": cmd.created_at.isoformat(),
        },
        status=201,
    )

