import React, { useState } from "react";
import { sendCommand } from "./api";

interface SimulationControlsProps {
  // No longer tracking state - just sending commands
}

// SVG Icons
const PlayIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 5v14l11-7z" />
  </svg>
);

const PauseIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
  </svg>
);

const StopIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 6h12v12H6z" />
  </svg>
);

const CheckIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
  </svg>
);

export const SimulationControls: React.FC<SimulationControlsProps> = () => {
  const [startTime, setStartTime] = useState<string>("");
  const [stepSize, setStepSize] = useState<number>(1);
  const [replaySpeed, setReplaySpeed] = useState<number>(1);
  const [busy, setBusy] = useState(false);

  const handleCommand = async (command: "start" | "pause" | "stop") => {
    setBusy(true);
    try {
      await sendCommand(command, {
        ...(startTime ? { start_time: startTime } : {}),
        step_size_seconds: stepSize,
        replay_speed: replaySpeed,
      });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Failed to send command", err);
    } finally {
      setBusy(false);
    }
  };

  const handleSetStartTime = async () => {
    if (!startTime) return;
    setBusy(true);
    try {
      await sendCommand("set_start_time", { start_time: startTime });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Failed to set start time", err);
    } finally {
      setBusy(false);
    }
  };

  const handleSetStepSize = async () => {
    setBusy(true);
    try {
      await sendCommand("set_step_size", { step_size_seconds: stepSize });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Failed to set step size", err);
    } finally {
      setBusy(false);
    }
  };

  const handleSetReplaySpeed = async () => {
    setBusy(true);
    try {
      await sendCommand("set_replay_speed", { replay_speed: replaySpeed });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Failed to set replay speed", err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="controls-panel">
      <h2>Simulation Controls</h2>
      <div className="controls-form">
        <label>
          <span>Start time (ISO-8601 UTC)</span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="text"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              placeholder="2026-01-27T12:00:00Z"
              style={{ flex: 1 }}
            />
            <button type="button" disabled={busy || !startTime} onClick={handleSetStartTime} style={{ padding: "0.5rem 1rem" }}>
              <CheckIcon />
            </button>
          </div>
        </label>
        <label>
          <span>Step size (seconds)</span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="number"
              min={0.1}
              step={0.1}
              value={stepSize}
              onChange={(e) => setStepSize(Number(e.target.value))}
              style={{ flex: 1 }}
            />
            <button type="button" disabled={busy} onClick={handleSetStepSize} style={{ padding: "0.5rem 1rem" }}>
              <CheckIcon />
            </button>
          </div>
        </label>
        <label>
          <span>Replay speed (x)</span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="number"
              min={0.1}
              step={0.1}
              value={replaySpeed}
              onChange={(e) => setReplaySpeed(Number(e.target.value))}
              style={{ flex: 1 }}
            />
            <button type="button" disabled={busy} onClick={handleSetReplaySpeed} style={{ padding: "0.5rem 1rem" }}>
              <CheckIcon />
            </button>
          </div>
        </label>
        <div className="button-row">
          <button type="button" disabled={busy} onClick={() => handleCommand("start")}>
            <PlayIcon />
            Start
          </button>
          <button type="button" disabled={busy} onClick={() => handleCommand("pause")}>
            <PauseIcon />
            Pause
          </button>
          <button type="button" disabled={busy} onClick={() => handleCommand("stop")}>
            <StopIcon />
            Stop
          </button>
        </div>
      </div>
    </div>
  );
};

