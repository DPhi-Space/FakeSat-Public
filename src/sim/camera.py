from pydispatch import dispatcher

TOPIC_SATELLITE_GROUND_POSITION = "satellite.ground_position"
TOPIC_SIMULATION_STEP_FORWARD = "simulation.step_forward"

class Camera:
    def __init__(self, shared_data_dict):
        dispatcher.connect(self.on_satellite_ground_position, signal=TOPIC_SATELLITE_GROUND_POSITION)
        self.current_satellite_position = (0.0, 0.0, 0.0)  # (lon, lat, alt)
        self.shared_data_dict = shared_data_dict

    def on_satellite_ground_position(self, sender, data, time):
        lon = data.get('lon', 0.0)
        lat = data.get('lat', 0.0)
        alt = data.get('alt', 0.0)
        self.current_satellite_position = (lon, lat, alt)
        self.shared_data_dict["satellite_position"] = self.current_satellite_position
        self.shared_data_dict["last_updated"] = time

