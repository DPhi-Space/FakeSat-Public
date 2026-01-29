from PIL import Image
import io
import matplotlib.pyplot as plt
from pystac_client import Client
import odc.stac
import numpy as np

class SentinelProvider:


    def __init__(self):
        self.client = Client.open("https://earth-search.aws.element84.com/v1")
        #self.bands = ['aot', 'blue', 'coastal', 'green', 'nir', 'nir08', 'nir09', 'red', 'rededge1', 'rededge2', 'rededge3', 'scl', 'swir16', 'swir22', 'visual', 'wvp']
        self.bands =  ['red', 'green', 'blue']

    def get_single_image_lon_lat(self, lon, lat, datetime, data_type="png"):
        # placeholder for datetime handling
        datetime = "2023-06-01/2023-06-30"

        bbox = self.get_bbox_around_lon_lat(lon, lat, image_size_km=10)

        image =  self.get_single_image_bbox(bbox, datetime, data_type=data_type)
        
        return image

    def get_single_image_bbox(self, bbox, datetime, data_type="png"):
        search = self.client.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=datetime,
            query={"eo:cloud_cover": {"lt": 100}},
            max_items=1
        )

        # Get the first item to extract metadata
        item = next(search.items())

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

        if data_type == "png":
            return self.image_to_png(image_data, bands=self.bands)
        else:
            return image_data
    
    # ------------------------------------
    # Helper Functions
    # ------------------------------------

    def get_bbox_around_lon_lat(self, lon, lat, image_size_km=1):
        """
        Create a bounding box (min_lon, min_lat, max_lon, max_lat) 
        around a given lon/lat point.
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Half the side length
        half_side = image_size_km / 2.0
        
        # Latitude offset (constant regardless of location)
        # 1 degree of lat is roughly 111km
        d_lat = np.degrees(half_side / R)
        
        # Longitude offset (varies based on latitude)
        # Shrinks by the cosine of the latitude
        d_lon = np.degrees(half_side / (R * np.cos(np.radians(lat))))
        
        min_lon = lon - d_lon
        max_lon = lon + d_lon
        min_lat = lat - d_lat
        max_lat = lat + d_lat
        
        return (min_lon, min_lat, max_lon, max_lat)
    
    def image_to_png(self, image_data, bands=['red', 'green', 'blue']):
        if len(bands) != 3 and len(bands) != 1:
            raise ValueError("bands parameter must contain exactly three or one band names for RGB image.")
        for band in bands:
            if band not in image_data.keys():
                raise ValueError(f"Band '{band}' is not available in the image data.")
            
        def scale_rgb_255(image_array):
            """Normalize 16-bit reflectance to 0-255 for display"""
            return (image_array / 3000 * 255).clip(0, 255).astype(np.uint8)
        
        array = scale_rgb_255(image_data[["red", "green", "blue"]].to_array().values.transpose(1, 2, 0))
        image = Image.fromarray(array)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0) # go to the beginning of the buffer
        return buffer

    

if __name__ == "__main__":
    provider = SentinelProvider()
    # Example coordinates (lofoten, norway)
    lon, lat = 14.1910, 68.1530
    image = provider.get_single_image_lon_lat(lon, lat, "2023-06-01/2023-06-30", data_type="png")
    img = plt.imread(image)
    plt.imshow(img)
    plt.axis('off')
    plt.show()