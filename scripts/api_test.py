# make the equivalent of curl http://127.0.0.1:8000/data/current/image/sentinel in python

import requests
import matplotlib.pyplot as plt
import xarray as xr
import base64
import numpy as np

def show_image(image_data):
    def scale_rgb(image_array):
        """Normalize 16-bit reflectance to 0-1 for display"""
        return (image_array / 3000).clip(0, 1)
    
    images = {}

    
    # create false color images using different band combinations
    # True Color (Red, Green, Blue)
    images['rgb'] = {'image': scale_rgb(image_data[["red", "green", "blue"]].to_array().values.transpose(1, 2, 0))}
    images['rgb']['description'] = "True Color (red, green, blue)"

    print(f"Prepared {len(images)} images for display.")

    if len(images) == 0:
        print("No images to display.")
        return
    elif len(images) == 1:
        key, img_info = next(iter(images.items()))
        plt.figure(figsize=(8, 8))
        plt.imshow(img_info['image'])
        plt.title(img_info['description'])
        plt.axis('off')
    else:
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

response = requests.get("http://localhost:9005/data/current/image/sentinel")

# check whether the request returned an error
if response.status_code != 200:
    print(f"Error: Received status code {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)


response_json = response.json()
meta = response_json['metadata']

# 1. Decode and reshape
raw_bytes = base64.b64decode(response_json['image'])
flat_array = np.frombuffer(raw_bytes, dtype=meta['dtype'])
reshaped_array = flat_array.reshape(meta['shape'])

# 2. Rebuild the Dataset
# We put it back into the (Band, Y, X) structure
image_xr = xr.DataArray(
    reshaped_array,
    dims=("band", "y", "x"),
    coords={"band": meta['bands']}
).to_dataset(dim="band")

# Now this will work!
show_image(image_xr)
