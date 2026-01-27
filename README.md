# FakeSat
Work in Progress

## Dataset Generation
The [Mapbox static images API](https://docs.mapbox.com/api/maps/static-images/) is used to generate earth observation satellite imagery of a given location, bearing, and pitch. A script is provided to generate a random dataset of images. 

Go to [mapbox.com](https://www.mapbox.com/) and create an account to get an access token. Set the environment variable `MAPBOX_ACCESS_TOKEN` to your access token.