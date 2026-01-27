from fastapi import FastAPI, Request, HTTPException
import io
import base64
import numpy as np
from ImagingProviders.sentinel_provider import SentinelProvider

api = FastAPI()

sentinel = SentinelProvider()


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




@api.get("/")
async def root():
    return {"message": "Simulation API is online"}