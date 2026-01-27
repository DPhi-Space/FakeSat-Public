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
  EllipsoidGeometry_default
} from "./chunk-C35SJ4QP.js";
import "./chunk-JERDRSEI.js";
import "./chunk-FM5XPC2E.js";
import "./chunk-JFN2DQHY.js";
import "./chunk-QO6Z5UJE.js";
import "./chunk-NY3CWLIZ.js";
import "./chunk-I45CATZK.js";
import "./chunk-JONWM4IO.js";
import "./chunk-7CDQUIP5.js";
import "./chunk-3JB2X2PR.js";
import "./chunk-SDUH3N6G.js";
import "./chunk-MWGB6DLR.js";
import "./chunk-N5MNKWED.js";
import "./chunk-FPRM6PCE.js";
import "./chunk-ZGWX2R5I.js";
import "./chunk-LDSQMLRC.js";
import "./chunk-WH4HDRGN.js";
import {
  defined_default
} from "./chunk-VSZ5DB2W.js";

// packages/engine/Source/Workers/createEllipsoidGeometry.js
function createEllipsoidGeometry(ellipsoidGeometry, offset) {
  if (defined_default(offset)) {
    ellipsoidGeometry = EllipsoidGeometry_default.unpack(ellipsoidGeometry, offset);
  }
  return EllipsoidGeometry_default.createGeometry(ellipsoidGeometry);
}
var createEllipsoidGeometry_default = createEllipsoidGeometry;
export {
  createEllipsoidGeometry_default as default
};
