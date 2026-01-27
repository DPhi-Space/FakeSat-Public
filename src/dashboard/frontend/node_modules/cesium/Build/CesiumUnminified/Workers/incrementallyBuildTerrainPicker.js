/**
 * @license
 * Cesium - https://github.com/CesiumGS/cesium
 * Version 1.137.0
 *
 * Copyright 2011-2022 Cesium Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Columbus View (Pat. Pend.)
 *
 * Portions licensed separately.
 * See https://github.com/CesiumGS/cesium/blob/main/LICENSE.md for full licensing details.
 */

import {
  createTaskProcessorWorker_default
} from "./chunk-XPNY2VY3.js";
import {
  AxisAlignedBoundingBox_default
} from "./chunk-BKYJBTHW.js";
import "./chunk-JONWM4IO.js";
import {
  Matrix4_default
} from "./chunk-3JB2X2PR.js";
import "./chunk-N5MNKWED.js";
import {
  Cartesian3_default
} from "./chunk-ZGWX2R5I.js";
import "./chunk-LDSQMLRC.js";
import "./chunk-WH4HDRGN.js";
import "./chunk-VSZ5DB2W.js";

// packages/engine/Source/Workers/incrementallyBuildTerrainPicker.js
var scratchAABBCornerMin = new Cartesian3_default();
var scratchAABBCornerMax = new Cartesian3_default();
var scratchTrianglePoints = [
  new Cartesian3_default(),
  new Cartesian3_default(),
  new Cartesian3_default()
];
var scratchTriangleAABB = new AxisAlignedBoundingBox_default();
function incrementallyBuildTerrainPicker(parameters, transferableObjects) {
  const aabbs = new Float64Array(parameters.aabbs);
  const nodeAABBs = Array.from({ length: 4 }, (_, i) => {
    const min = Cartesian3_default.unpack(aabbs, i * 6, scratchAABBCornerMin);
    const max = Cartesian3_default.unpack(aabbs, i * 6 + 3, scratchAABBCornerMax);
    return AxisAlignedBoundingBox_default.fromCorners(
      min,
      max,
      new AxisAlignedBoundingBox_default()
    );
  });
  const inverseTransformArray = new Float64Array(parameters.inverseTransform);
  const inverseTransform = Matrix4_default.unpack(
    inverseTransformArray,
    0,
    new Matrix4_default()
  );
  const triangleIndices = new Uint32Array(parameters.triangleIndices);
  const trianglePositions = new Float32Array(parameters.trianglePositions);
  const intersectingTrianglesArrays = Array.from({ length: 4 }, () => []);
  for (let j = 0; j < triangleIndices.length; j++) {
    Cartesian3_default.unpack(trianglePositions, j * 9, scratchTrianglePoints[0]);
    Cartesian3_default.unpack(trianglePositions, j * 9 + 3, scratchTrianglePoints[1]);
    Cartesian3_default.unpack(trianglePositions, j * 9 + 6, scratchTrianglePoints[2]);
    const triangleAABB = createAABBFromTriangle(
      inverseTransform,
      scratchTrianglePoints
    );
    for (let i = 0; i < 4; i++) {
      const aabbsIntersect = nodeAABBs[i].intersectAxisAlignedBoundingBox(triangleAABB);
      if (!aabbsIntersect) {
        continue;
      }
      intersectingTrianglesArrays[i].push(triangleIndices[j]);
    }
  }
  const intersectingTrianglesTypedArrays = intersectingTrianglesArrays.map(
    (array) => {
      const uintArray = new Uint32Array(array);
      transferableObjects.push(uintArray.buffer);
      return uintArray.buffer;
    }
  );
  return {
    intersectingTrianglesArrays: intersectingTrianglesTypedArrays
  };
}
function createAABBFromTriangle(inverseTransform, trianglePoints) {
  Matrix4_default.multiplyByPoint(
    inverseTransform,
    trianglePoints[0],
    trianglePoints[0]
  );
  Matrix4_default.multiplyByPoint(
    inverseTransform,
    trianglePoints[1],
    trianglePoints[1]
  );
  Matrix4_default.multiplyByPoint(
    inverseTransform,
    trianglePoints[2],
    trianglePoints[2]
  );
  return AxisAlignedBoundingBox_default.fromPoints(trianglePoints, scratchTriangleAABB);
}
var incrementallyBuildTerrainPicker_default = createTaskProcessorWorker_default(incrementallyBuildTerrainPicker);
export {
  incrementallyBuildTerrainPicker_default as default
};
