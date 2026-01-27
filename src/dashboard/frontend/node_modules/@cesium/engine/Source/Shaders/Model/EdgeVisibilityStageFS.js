//This file is automatically rebuilt by the Cesium build process.
export default "// CESIUM_REDIRECTED_COLOR_OUTPUT flag is used to avoid color attachment conflicts\n\
// when shaders are processed by different rendering pipelines (e.g., OIT).\n\
// Only declare MRT outputs when not in a derived shader context.\n\
#if defined(HAS_EDGE_VISIBILITY_MRT) && !defined(CESIUM_REDIRECTED_COLOR_OUTPUT)\n\
layout(location = 1) out vec4 out_id;        // edge id / metadata\n\
layout(location = 2) out vec4 out_edgeDepth; // packed depth\n\
#endif\n\
\n\
void edgeVisibilityStage(inout vec4 color, inout FeatureIds featureIds)\n\
{\n\
#ifdef HAS_EDGE_VISIBILITY\n\
\n\
    if (!u_isEdgePass) {\n\
        return;\n\
    }\n\
    \n\
    float edgeTypeInt = v_edgeType * 255.0;\n\
    \n\
    // Color code different edge types\n\
    vec4 edgeColor = vec4(0.0);\n\
    \n\
    if (edgeTypeInt < 0.5) { // HIDDEN (0)\n\
        edgeColor = vec4(0.0, 0.0, 0.0, 0.0); // Transparent for hidden edges\n\
    }\n\
    else if (edgeTypeInt > 0.5 && edgeTypeInt < 1.5) { // SILHOUETTE (1) - Conditional visibility\n\
        // Proper silhouette detection using face normals\n\
        vec3 normalA = normalize(v_faceNormalAView);\n\
        vec3 normalB = normalize(v_faceNormalBView);\n\
        \n\
        // Calculate view direction using existing eye-space position varying (v_positionEC)\n\
        vec3 viewDir = -normalize(v_positionEC);\n\
        \n\
        // Calculate dot products to determine triangle facing\n\
        float dotA = dot(normalA, viewDir);\n\
        float dotB = dot(normalB, viewDir);\n\
        \n\
        const float eps = 1e-3;\n\
        bool frontA = dotA > eps;\n\
        bool backA  = dotA < -eps;\n\
        bool frontB = dotB > eps;\n\
        bool backB  = dotB < -eps;\n\
        \n\
        // True silhouette: one triangle front-facing, other back-facing\n\
        bool oppositeFacing = (frontA && backB) || (backA && frontB);\n\
        \n\
        // Exclude edges where both triangles are nearly grazing (perpendicular to view)\n\
        // This handles the top-view cylinder case where both normals are ~horizontal\n\
        bool bothNearGrazing = (abs(dotA) <= eps && abs(dotB) <= eps);\n\
        \n\
        if (!(oppositeFacing && !bothNearGrazing)) {\n\
            discard; // Not a true silhouette edge\n\
        } else {\n\
            // True silhouette\n\
            edgeColor = vec4(1.0, 0.0, 0.0, 1.0);\n\
        }\n\
    }\n\
    else if (edgeTypeInt > 1.5 && edgeTypeInt < 2.5) { // HARD (2) - BRIGHT GREEN\n\
        edgeColor = vec4(0.0, 1.0, 0.0, 1.0); // Extra bright green\n\
    }\n\
    else if (edgeTypeInt > 2.5 && edgeTypeInt < 3.5) { // REPEATED (3)\n\
        edgeColor = vec4(0.0, 0.0, 1.0, 1.0);\n\
    } else {\n\
        edgeColor = vec4(0.0, 0.0, 0.0, 0.0);\n\
    }\n\
\n\
    // Temporary color: white\n\
    edgeColor = vec4(1.0, 1.0, 1.0, 1.0);\n\
    color = edgeColor;\n\
    \n\
    #if defined(HAS_EDGE_VISIBILITY_MRT) && !defined(CESIUM_REDIRECTED_COLOR_OUTPUT)\n\
        // Write edge metadata\n\
        out_id = vec4(0.0);\n\
        out_id.r = edgeTypeInt;                    // Edge type (0-3)\n\
#ifdef HAS_EDGE_FEATURE_ID\n\
        out_id.g = float(featureIds.featureId_0); // Feature ID if available\n\
#else\n\
        out_id.g = 0.0;\n\
#endif\n\
        // Pack depth into separate MRT attachment\n\
        out_edgeDepth = czm_packDepth(gl_FragCoord.z);\n\
    #endif\n\
#endif\n\
}\n\
";
