import obsws_python as obs
import time

class OBSController:
    def __init__(self, host='localhost', port=4455, password='', timeout=5):
        """Initialize and connect to the OBS WebSockets server."""
        try:
            self.ws = obs.ReqClient(host=host, port=port, password=password)
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")

    @staticmethod
    def _print_object_attributes(obj):
        """Internal method to print attributes of an object."""
        for attribute_name in dir(obj):
            attribute_value = getattr(obj, attribute_name)
            if not callable(attribute_value) and not attribute_name.startswith("__"):
                print(attribute_name, ":", attribute_value)

    def print_scene_item_transform(self, scene_name, source_name):
        """Fetch and print the transform details of a source in a scene."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            transform_details = self.ws.get_scene_item_transform(scene_name, source_id)
            self._print_object_attributes(transform_details)
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")

    def get_source_id_by_name(self, scene_name, source_name):
        """Fetches the ID of a source in a scene by its name."""
        scene_details = self.ws.get_scene_item_list(scene_name)
        for item in scene_details.scene_items:
            if item['sourceName'] == source_name:
                return item['sceneItemId']
        return None

    def set_source_enabled_by_name(self, scene_name, source_name, enable):
        """Enable or disable a source using its name."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            self.ws.set_scene_item_enabled(scene_name, source_id, enable)
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")

    def get_source_enabled_by_name(self, scene_name, source_name):
        """Get the enabled status of a source using its name."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            scene_details = self.ws.get_scene_item_list(scene_name)
            for item in scene_details.scene_items:
                if item['sceneItemId'] == source_id:
                    return item['sceneItemEnabled']  # Assuming 'visible' is the attribute for enabled status
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")
        return None  # Return None if source not found or any other error occurs

    def set_transform_by_source_name(self, scene_name, source_name, transform):
        """Modify the transform attributes of a source using its name."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            try:
                self.ws.set_scene_item_transform(scene_name, source_id, transform)
            except Exception as e:
                print(f"Failed to modify the source transform: {e}")
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")

    def get_transform_by_source_name(self, scene_name, source_name):
        """Fetch the transform attributes of a source using its name."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            try:
                transform_dataclass = self.ws.get_scene_item_transform(scene_name, source_id)
                if hasattr(transform_dataclass, 'scene_item_transform'):
                    return transform_dataclass.scene_item_transform
                else:
                    print(f"scene_item_transform not found in the returned dataclass for source '{source_name}'.")
                    return None
            except Exception as e:
                print(f"Failed to fetch the source transform: {e}")
                return None
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")
            return None

    def slide_source(self, scene_name, source_name, end_position, duration):
        """
        Slide a source from its current position to the specified end_position over the given duration.

        :param scene_name: Name of the scene containing the source.
        :param source_name: Name of the source to be moved.
        :param end_position: Tuple (x, y) specifying the end position for the slide.
        :param duration: Duration of the slide animation in seconds.
        """
        # Get the current position of the source.
        current_transform = self.get_transform_by_source_name(scene_name, source_name)
        if not current_transform:
            print(f"Failed to get the transform for source '{source_name}'.")
            return

        start_position = (current_transform["positionX"], current_transform["positionY"])

        # Ensure required fields have valid values
        current_transform["boundsWidth"] = max(1.0, current_transform.get("boundsWidth", 1.0))
        current_transform["boundsHeight"] = max(1.0, current_transform.get("boundsHeight", 1.0))

        # Calculate the step size for both x and y directions based on the duration.
        fps = 60  # Target frames per second
        steps = int(fps * duration)  # Total number of steps in the animation
        step_duration = duration / steps
        x_step = (end_position[0] - start_position[0]) / steps
        y_step = (end_position[1] - start_position[1]) / steps

        # Periodically update the source's position while retaining all other transform attributes.
        for step in range(steps):
            new_transform = {
                **current_transform,  # First retain all other transform attributes
                "positionX": start_position[0] + x_step * (step + 1),
                "positionY": start_position[1] + y_step * (step + 1)
            }
            self.set_transform_by_source_name(scene_name, source_name, new_transform)

            # Ensure smooth animation by using time.sleep between updates.
            time.sleep(step_duration)

        # Ensure the source is exactly at the end_position at the end of the animation.
        current_transform["positionX"] = end_position[0]
        current_transform["positionY"] = end_position[1]
        self.set_transform_by_source_name(scene_name, source_name, current_transform)


    def set_source_opacity(self, scene_name, source_name, opacity):
        """Set the opacity of a source."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            current_transform = self.get_transform_by_source_name(scene_name, source_name)
            if current_transform is not None:
                new_transform = {
                    **current_transform,
                    'opacity': opacity
                }
                self.set_transform_by_source_name(scene_name, source_name, new_transform)
            else:
                print(f"Failed to fetch current transform for source '{source_name}' in scene '{scene_name}'.")
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")

    def set_source_zoom(self, scene_name, source_name, zoom_level):
        """Set the zoom level of a source."""
        source_id = self.get_source_id_by_name(scene_name, source_name)
        if source_id:
            current_transform = self.get_transform_by_source_name(scene_name, source_name)
            if current_transform is not None:
                # Assuming width and height are the keys for the current size of the source
                new_width = current_transform['width'] * zoom_level
                new_height = current_transform['height'] * zoom_level
                new_transform = {
                    **current_transform,
                    'width': new_width,
                    'height': new_height
                }
                self.set_transform_by_source_name(scene_name, source_name, new_transform)
            else:
                print(f"Failed to fetch current transform for source '{source_name}' in scene '{scene_name}'.")
        else:
            print(f"Source '{source_name}' not found in scene '{scene_name}'.")

    def fetch_sources(self, scene_name):
        """Fetch the list of sources from a specified scene."""
        try:
            scene_details = self.ws.get_scene_item_list(scene_name)  # Use the get_scene_item_list function
            # Check if scene_details has a scene_items attribute
            if hasattr(scene_details, 'scene_items'):
                # Use scene_items attribute and return a list of source names
                return [item['sourceName'] for item in scene_details.scene_items]
            else:
                print(f"Failed to fetch sources for scene '{scene_name}'.")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def pause_media_source(self, source_name):
        """Pause a media source."""
        try:
            self.ws.trigger_media_input_action(source_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE")
        except Exception as e:
            print(f"Failed to pause media source '{source_name}': {e}")

    def play_media_source(self, source_name):
        """Play (or resume) a media source."""
        try:
            self.ws.trigger_media_input_action(source_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY")
        except Exception as e:
            print(f"Failed to play media source '{source_name}': {e}")

    # FILTER MODIFICATION HERE

    def set_filter_enabled(self, source_name, filter_name, enable):
        """
        Enable or disable a filter on a specific source.
        
        :param source_name: Name of the source.
        :param filter_name: Name of the filter.
        :param enable: Boolean value to enable or disable the filter.
        """
        try:
            self.ws.set_source_filter_enabled(source_name, filter_name, enable)
        except Exception as e:
            print(f"Failed to set filter '{filter_name}' enabled state on source '{source_name}': {e}")

    def get_source_filters(self, source_name):
        """
        Get a list of filters applied to a specific source.
    
        :param source_name: Name of the source.
        :return: List of filters or None if an error occurred.
        """
        try:
            filter_list_data = self.ws.get_source_filter_list(source_name)
            return filter_list_data.filters  # Assumes GetSourceFilterListDataclass has a filters attribute
        except Exception as e:
            print(f"Failed to get filters for source '{source_name}': {e}")
            return None


    def toggle_filter_on_source(self, source_name, filter_name):
        """Toggle the enabled state of a filter on a specific source."""
        try:
            current_filters = self.ws.get_source_filters(source_name)
            for filter_info in current_filters:
                if filter_info['name'] == filter_name:
                    new_state = not filter_info['enabled']
                    self.ws.set_source_filter_enabled(source_name, filter_name, new_state)
                    return  # Exit once the filter is found and toggled
            print(f"Filter '{filter_name}' not found on source '{source_name}'.")
        except Exception as e:
            print(f"Failed to toggle filter '{filter_name}' on source '{source_name}': {e}")

    def set_source_filter_settings(self, source_name, filter_name, filter_settings):
        """Modify the settings of a filter on a specific source."""
        try:
            self.ws.set_source_filter_settings(source_name, filter_name, filter_settings)
        except Exception as e:
            print(f"Failed to set filter settings for filter '{filter_name}' on source '{source_name}': {e}")

    def add_filter_to_source(self, source_name, filter_name, filter_type, filter_settings):
        """Add a new filter to a specific source."""
        try:
            self.ws.create_source_filter(source_name, filter_name, filter_type, filter_settings)
        except Exception as e:
            print(f"Failed to add filter '{filter_name}' to source '{source_name}': {e}")

    def remove_filter_from_source(self, source_name, filter_name):
        """Remove a filter from a specific source."""
        try:
            self.ws.remove_source_filter(source_name, filter_name)
        except Exception as e:
            print(f"Failed to remove filter '{filter_name}' from source '{source_name}': {e}")
    
    def reorder_source_filter(self, source_name, filter_name, new_index):
        """Reorder a filter on a specific source."""
        try:
            self.ws.set_source_filter_index(source_name, filter_name, new_index)
        except Exception as e:
            print(f"Failed to reorder filter '{filter_name}' on source '{source_name}': {e}")

    ### SCREENSHOT FUNCTIONS SIMPLIFIED, CONSIDER ADDING IN WIDTH/HEIGHT, QUALITY + FILE PATH OPTIONS

    def get_source_screenshot(self, source_name, img_format, width, height, quality):
        """Takes a base64 encoded screenshot of a given source"""
        try:
            self.ws.get_source_screenshot(source_name, img_format, width, height, quality)
        except Exception as e:
            print(f"Failed to grab screenshot of source '{source_name}': {e}")

    def save_source_screenshot(self, source_name, img_format, file_path, width, height, quality):
        """Saves a base64 encoded screenshot of a given source"""
        try:
            self.ws.save_source_screenshot(source_name, img_format, file_path, width, height, quality)
        except Exception as e:
            print(f"Failed to grab screenshot of source '{source_name}': {e}")





