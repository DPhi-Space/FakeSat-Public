import axios from "axios";

export interface TelemetryPoint {
  satellite: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  altitude: number | null;
  extra: unknown;
}

export interface Command {
  command: "start" | "pause" | "stop" | "set_start_time" | "set_step_size" | "set_replay_speed";
  parameters: {
    start_time?: string;
    step_size_seconds?: number;
    replay_speed?: number;
  };
}

const api = axios.create({
  baseURL: "/api",
});

export async function fetchRecentTelemetry(): Promise<TelemetryPoint[]> {
  const res = await api.get<{ telemetry: TelemetryPoint[] }>("/telemetry/recent/");
  return res.data.telemetry ?? [];
}

export async function sendCommand(
  command: Command["command"],
  parameters?: Command["parameters"]
): Promise<{ id: number; command: string; parameters: Record<string, unknown>; created_at: string }> {
  const res = await api.post("/commands/", {
    command,
    ...(parameters || {}),
  });
  return res.data;
}

