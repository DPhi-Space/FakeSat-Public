import React from "react";
import type { TelemetryPoint } from "./api";

interface TelemetryPanelProps {
  latest: TelemetryPoint | null;
}

const formatTime = (isoString: string | null): string => {
  if (!isoString) return "—";
  try {
    const date = new Date(isoString);
    return date.toISOString().replace("T", " ").substring(0, 19) + " UTC";
  } catch {
    return isoString;
  }
};

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ latest }) => {
  const simTime = latest?.timestamp ?? null;

  return (
    <div className="telemetry-panel">
      <h2>Telemetry</h2>
      {latest ? (
        <div className="telemetry-grid">
          <div>
            <span className="label">Satellite</span>
            <span className="value">{latest.satellite}</span>
          </div>
          <div>
            <span className="label">Latitude</span>
            <span className="value">{latest.latitude.toFixed(4)}°</span>
          </div>
          <div>
            <span className="label">Longitude</span>
            <span className="value">{latest.longitude.toFixed(4)}°</span>
          </div>
          <div>
            <span className="label">Altitude</span>
            <span className="value">{latest.altitude != null ? `${latest.altitude.toFixed(2)} km` : "—"}</span>
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <span className="label">Simulation Time (UTC)</span>
            <span className="value" style={{ fontSize: "0.85rem", fontFamily: "monospace" }}>
              {formatTime(simTime)}
            </span>
          </div>
        </div>
      ) : (
        <p>No telemetry received yet.</p>
      )}
    </div>
  );
};

