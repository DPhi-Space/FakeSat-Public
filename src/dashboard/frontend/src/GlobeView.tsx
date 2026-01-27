import React, { useEffect, useRef } from "react";
import type { TelemetryPoint } from "./api";
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

interface GlobeViewProps {
  telemetry: TelemetryPoint[];
}

export const GlobeView: React.FC<GlobeViewProps> = ({ telemetry }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Load Cesium assets (Workers, Assets, Widgets) from our own static path
    (window as any).CESIUM_BASE_URL = "/static/cesium/";

    const viewer = new Cesium.Viewer(containerRef.current, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      fullscreenButton: false,
      terrainProvider: new Cesium.EllipsoidTerrainProvider(),
    });

    // Remove the default blue sky/atmosphere
    viewer.scene.skyBox.show = false;
    viewer.scene.skyAtmosphere.show = false;
    
    // Remove default imagery and add satellite imagery
    viewer.imageryLayers.removeAll();
    
    // Use a satellite imagery tile service that works reliably with Cesium
    // Using Esri World Imagery via tile URL format (more reliable than MapServer)
    viewer.imageryLayers.addImageryProvider(
      new Cesium.UrlTemplateImageryProvider({
        url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        credit: "© Esri",
        maximumLevel: 19,
      })
    );

    // Set camera to show Earth nicely
    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(0, 0, 15000000),
    });

    viewerRef.current = viewer;

    telemetry.forEach((point) => {
      viewer.entities.add({
        id: point.satellite,
        position: Cesium.Cartesian3.fromDegrees(
          point.longitude,
          point.latitude,
          (point.altitude ?? 0) * 1000,
        ),
        point: {
          pixelSize: 10,
          color: Cesium.Color.CYAN,
        },
      });
    });

    return () => {
      if (viewerRef.current && !viewerRef.current.isDestroyed && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update entities as telemetry changes
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !telemetry.length) return;

    telemetry.forEach((point) => {
      let entity = viewer.entities.getById(point.satellite);
      const position = Cesium.Cartesian3.fromDegrees(
        point.longitude,
        point.latitude,
        (point.altitude ?? 0) * 1000,
      );

      if (!entity) {
        entity = viewer.entities.add({
          id: point.satellite,
          position,
          point: {
            pixelSize: 10,
            color: Cesium.Color.CYAN,
          },
        });
      } else {
        entity.position = position;
      }
    });
  }, [telemetry]);

  return <div ref={containerRef} className="globe-view" />;
};

