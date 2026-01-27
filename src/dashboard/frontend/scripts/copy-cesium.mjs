import { cpSync, existsSync, mkdirSync } from "fs";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const projectRoot = resolve(__dirname, "..");
const cesiumSource = resolve(projectRoot, "node_modules", "cesium", "Build", "Cesium");
const cesiumDest = resolve(projectRoot, "dist", "cesium");

if (!existsSync(cesiumSource)) {
  console.error("Cesium source folder not found:", cesiumSource);
  process.exit(1);
}

if (!existsSync(cesiumDest)) {
  mkdirSync(cesiumDest, { recursive: true });
}

console.log("Copying Cesium from", cesiumSource, "to", cesiumDest);
cpSync(cesiumSource, cesiumDest, { recursive: true });
console.log("Cesium assets copied successfully.");
