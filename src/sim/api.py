from fastapi import FastAPI, Request, HTTPException, Query, Response
import io
import base64
import numpy as np
from ImagingProviders.sentinel_provider import SentinelProvider
from ImagingProviders.mapbox_provider import MapboxlProvider

api = FastAPI()

sentinel = SentinelProvider()
mapbox = MapboxlProvider()


def serialize_xarray_dataset(ds):
    da = ds.to_array()
    metadata = {
        "shape": da.shape,        # e.g., (3, 512, 512)
        "dtype": str(da.dtype),   # e.g., "uint16" or "float32"
        "bands": list(ds.data_vars) # e.g., ["red", "green", "blue"]
    }
    image_bytes = da.values.tobytes()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return {
        "metadata": metadata,
        "image": image_b64
    }

@api.get("/data/current/position")
async def get_metrics():
    # We access the shared data that the orchestrator will inject
    data = getattr(api.state, "shared_data", {})
    return {
        "lon-lat-alt": data.get("satellite_position", [0, 0, 0]),
        "timestamp": data.get("last_updated", 0)
    }


@api.get("/data/current/image/sentinel")
async def get_sentinel_image():
    data = getattr(api.state, "shared_data", {}).get("satellite_position", None)
    # if data is none return an error
    if data is None:
        raise HTTPException(status_code=500, detail="No image data available")
    
    try:
        data = sentinel.get_single_image_lon_lat(data[0], data[1], "2023-06-01/2023-06-30")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching Sentinel image: " + str(e))
    image = serialize_xarray_dataset(data["image"])
    return image

@api.get("/data/current/image/mapbox")
async def get_mapbox_image(
    lat: float = Query(..., description="The latitude of the location", ge=-90, le=90),
    lon: float = Query(..., description="The longitude of the location", sw=-180, le=180)
):
    try:
        satellite_position = getattr(api.state, "shared_data", {}).get("satellite_position", None)
        image = mapbox.get_target_image(satellite_position[0], satellite_position[1], satellite_position[2], lon, lat)
        
        return Response(content=image, media_type="image/png")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error fetching Mapbox image: " + str(e))


@api.get("/")
async def root():
    return {"message": "Simulation API is online"}