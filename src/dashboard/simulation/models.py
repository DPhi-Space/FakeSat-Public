from __future__ import annotations

from django.db import models


class Satellite(models.Model):
    """
    Basic satellite metadata.
    """

    name = models.CharField(max_length=128, unique=True)
    norad_id = models.CharField(max_length=32, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Telemetry(models.Model):
    """
    Latest telemetry for a satellite (one record per satellite, always updated).
    
    Stores only the most recently pushed position, regardless of timestamp.
    """

    satellite = models.OneToOneField(
        Satellite,
        on_delete=models.CASCADE,
        related_name="latest_telemetry",
        primary_key=True,
        help_text="One telemetry record per satellite (always the latest pushed)",
    )
    timestamp = models.DateTimeField(help_text="Simulation timestamp (UTC).")
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True, help_text="Altitude in kilometers.")
    extra = models.JSONField(null=True, blank=True, help_text="Future telemetry fields.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this telemetry was last updated (pushed)")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "Telemetry"

    def __str__(self) -> str:
        return f"{self.satellite} @ {self.timestamp.isoformat()}"


class SimulationCommand(models.Model):
    """
    Command queue for simulation control.
    
    The dashboard adds commands here, and the simulator polls /api/commands/
    to get all commands since the last poll, then they are marked as consumed.
    """

    COMMAND_TYPES = [
        ("start", "Start simulation"),
        ("pause", "Pause simulation"),
        ("stop", "Stop simulation"),
        ("set_start_time", "Set simulation start time"),
        ("set_step_size", "Set step size"),
        ("set_replay_speed", "Set replay speed"),
    ]

    command_type = models.CharField(max_length=32, choices=COMMAND_TYPES)
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Command-specific parameters (e.g., start_time, step_size, replay_speed)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    consumed = models.BooleanField(default=False, help_text="True when simulator has fetched this command")

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["consumed", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.command_type} @ {self.created_at.isoformat()}"

    def to_dict(self) -> dict:
        """Convert command to JSON-serializable dict."""
        return {
            "command": self.command_type,
            "parameters": self.parameters or {},
        }

