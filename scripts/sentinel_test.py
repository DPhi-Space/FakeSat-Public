"""
This script connects to the Sentinel-2 STAC API, retrieves a single cloud-free image over a specified area and time. 
This is the basis for future work.
"""


import matplotlib.pyplot as plt
from pystac_client import Client
import odc.stac
import numpy as np


BANDS = ['aot', 'blue', 'coastal', 'green', 'nir', 'nir08', 'nir09', 'red', 'rededge1', 'rededge2', 'rededge3', 'scl', 'swir16', 'swir22', 'visual', 'wvp']
jp2_bands = ['aot-jp2', 'blue-jp2', 'coastal-jp2', 'green-jp2', 'nir-jp2', 'nir08-jp2', 'nir09-jp2', 'red-jp2', 'rededge1-jp2', 'rededge2-jp2', 'rededge3-jp2', 'scl-jp2', 'swir16-jp2', 'swir22-jp2', 'visual-jp2', 'wvp-jp2']
# 1. Connect and Search
client = Client.open("https://earth-search.aws.element84.com/v1")
bbox = [6.5683, 46.4768, 6.6983, 46.5668]

def get_single_image():
    search = client.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2023-06-01/2023-06-30", # Early summer for greenest vegetation
        query={"eo:cloud_cover": {"lt": 5}},
        max_items=1
    )

    # Get the first item to extract metadata
    item = next(search.get_items())

    # 2. Print Metadata
    print("--- METADATA ---")
    print(f"ID: {item.id}")
    print(f"Date: {item.datetime}")
    print(f"Cloud Cover: {item.properties['eo:cloud_cover']}%")
    print(f"Platform: {item.properties['platform']}")
    print(f"Available Bands: {list(item.assets.keys())}")
    print("-" * 15)

    # 3. Load all 13 Spectral Bands
    #bands_to_load = ["blue", "green", "red", "nir", "swir16", "swir22"]
    image_data = odc.stac.load(
        [item],
        bands=BANDS,
        bbox=bbox,
        resolution=10, # Note: Coarser bands will be upsampled to 10m
        chunks={"x": 2048, "y": 2048}
    ).isel(time=0)

    return image_data


def show_image(image_data):
    def scale_rgb(image_array):
        """Normalize 16-bit reflectance to 0-1 for display"""
        return (image_array / 3000).clip(0, 1)
    
    images = {}

    # create single channel images
    for band in BANDS:
        band_data = image_data[band]
        if np.nanmax(band_data) > 0:
            images[band] = {'image': scale_rgb(band_data)}
            images[band]['description'] = f"Band: {band}"
            print(f"Prepared single band image for {band}")


    # create false color images using different band combinations
    # True Color (Red, Green, Blue)
    images['rgb'] = {'image': scale_rgb(image_data[["red", "green", "blue"]].to_array().values.transpose(1, 2, 0))}
    images['rgb']['description'] = "True Color (red, green, blue)"
    # traditional NIR image. healthy plants reflect NIR and are therefore  a strong red. Allows to see different vegetation. Bright red = healthy forest/crops; Dull red = grasslands; Cyan/Grey = buildings and other non-vegetated surfaces
    images['tnir'] = {'image': scale_rgb(image_data[["nir", "red", "green"]].to_array().values.transpose(1, 2, 0))}
    images['tnir']['description'] = "Traditional NIR (nir, red, green)"
    # SWIR (showrt-wave infrared): sensiteive to water and water. Deep green indicates lush, water-rich vegetation. Very dark blue/black indicates clear water.
    images['swir'] = {'image': scale_rgb(image_data[["swir22", "nir", "green"]].to_array().values.transpose(1, 2, 0))}
    images['swir']['description'] = "SWIR (swir22, nir, green)"
    # urban false color with swire22, swir16, red: This combination "sees" through atmospheric haze and smoke much better than visible light. Urban areas and bare soil pop in shades of purple and brown, while vegetation appears in green.
    images['ufc'] = {'image': scale_rgb(image_data[["swir22", "swir16", "red"]].to_array().values.transpose(1, 2, 0))}
    images['ufc']['description'] = "Urban False Color (swir22, swir16, red)"
    # vegetation index: rededge3, rededge2, rededge1 Sentinel-2 is unique because of these three "Red Edge" bands. They capture the specific point where plant reflectance jumps. Precision agriculture and detecting early-stage plant stress before it’s visible in RGB. Color differences indicate differences in platn health/development.
    images['vi'] = {'image': scale_rgb(image_data[["rededge3", "rededge2", "rededge1"]].to_array().values.transpose(1, 2, 0))}
    images['vi']['description'] = "Vegetation Index (rededge3, rededge2, rededge1)"

    print(f"Prepared {len(images)} images for display.")

    n_cols = min(5, len(images))
    n_rows = (len(images) + n_cols - 1) // n_cols
    fig, ax = plt.subplots(n_rows, n_cols, figsize=(20, 10))

    for i, (key, img_info) in enumerate(images.items()):
        r = i // n_cols
        c = i % n_cols
        ax[r, c].imshow(img_info['image'])
        ax[r, c].set_title(img_info['description'])
        ax[r, c].axis('off')

    plt.tight_layout()
    print("Displaying images...")
    plt.show()



if __name__ == "__main__":
    data = get_single_image()
    show_image(data)