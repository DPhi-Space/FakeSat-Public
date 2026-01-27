import matplotlib.pyplot as plt
from pystac_client import Client
import odc.stac
import numpy as np

class SentinelProvider:

    def __init__(self):
        self.client = Client.open("https://earth-search.aws.element84.com/v1")
        #self.bands = ['aot', 'blue', 'coastal', 'green', 'nir', 'nir08', 'nir09', 'red', 'rededge1', 'rededge2', 'rededge3', 'scl', 'swir16', 'swir22', 'visual', 'wvp']
        self.bands =  ['red', 'green', 'blue']

    def get_single_image_lon_lat(self, lon, lat, datetime):
        # Define a small bounding box around the lon/lat
        delta = 0.1  # ~10km
        lon = float(lon)
        lat = float(lat)
        bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
        #print(bbox)
        #bbox = [6.5683, 46.4768, 6.6983, 46.5668]
        print(bbox)
        print(datetime)

        image =  self.get_single_image_bbox(bbox, datetime)
        return {
            "image": image,
            "bbox": bbox,
            "timestamp": datetime
        }

    def get_single_image_bbox(self, bbox, datetime):
        search = self.client.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=datetime,
            query={"eo:cloud_cover": {"lt": 100}},
            max_items=1
        )

        # Get the first item to extract metadata
        item = next(search.get_items())

        metadata = {
            "id": item.id,
            "date": item.datetime,
            "cloud_cover": item.properties['eo:cloud_cover'],
            "platform": item.properties['platform'],
            "available_bands": list(item.assets.keys())
        }

        image_data = odc.stac.load(
            [item],
            bands=self.bands,
            bbox=bbox,
            resolution=10, # Note: Coarser bands will be upsampled to 10m
            chunks={"x": 2048, "y": 2048}
        ).isel(time=0)

        return image_data
