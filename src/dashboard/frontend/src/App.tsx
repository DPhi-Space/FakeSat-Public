import React, { useEffect, useState } from "react";
import { TelemetryPoint, fetchRecentTelemetry } from "./api";
import { GlobeView } from "./GlobeView";
import { TelemetryPanel } from "./TelemetryPanel";
import { SimulationControls } from "./SimulationControls";

export const App: React.FC = () => {
  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>([]);

  // Poll telemetry ~1 Hz
  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const data = await fetchRecentTelemetry();
        if (!cancelled) {
          setTelemetry(data);
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error("Failed to fetch telemetry", err);
      }
    };

    poll();
    const handle = setInterval(poll, 1000);

    return () => {
      cancelled = true;
      clearInterval(handle);
    };
  }, []);

  const latest = telemetry[0] ?? null;

  return (
    <div className="app">
      <header className="app-header">
        <h1>Satellite Simulation Dashboard</h1>
      </header>
      <main className="app-main">
        <section className="globe-section">
          <GlobeView telemetry={telemetry} />
        </section>
        <section className="side-panel">
          <TelemetryPanel latest={latest} />
          <SimulationControls />
        </section>
      </main>
    </div>
  );
};

