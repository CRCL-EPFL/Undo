import Metashape
import os

# Define paths
image_folder = "C:/Users/eleni/Desktop/scan/scan_state_C"  # Change this to your image folder
project_path = "K:/.shortcut-targets-by-id/1IiGhZQRuFujGaxqXg4taUaPR55vt4fB7/DMS 2024/06_RobotFiles/metashape/state_C.psx"   # Path to save the Metashape project file
point_cloud_path = "K:/.shortcut-targets-by-id/1IiGhZQRuFujGaxqXg4taUaPR55vt4fB7/DMS 2024/06_RobotFiles/metashape/automated_state_C.ply"  # Path to export the point cloud as a .ply file

# Open or create a new Metashape project
doc = Metashape.Document()
doc.save(project_path)

# Create a new chunk
chunk = doc.addChunk()

# Add images from folder
image_list = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.lower().endswith(('jpg', 'jpeg', 'tif', 'png'))]
chunk.addPhotos(image_list)

# Detect markers
chunk.detectMarkers(Metashape.TargetType.CircularTarget12bit, tolerance=50)

# Align cameras
chunk.matchPhotos(generic_preselection=True, filter_stationary_points=True, keypoint_limit=40000, tiepoint_limit=40000)
chunk.alignCameras()

aligned_cameras = [camera for camera in chunk.cameras if camera.transform is not None]
print (str(len(aligned_cameras)) + " cameras were aligned")

# Add marker coordinates manually
# These are hypothetical marker coordinates; adjust them to match your own
# Replace marker_index with the index of the marker you want to set coordinates for
markers = chunk.markers

marker_coordinates = {
    73: (2.131,0.192,0.222),
    74: (2.118,1.577,0.222),
    75: (0.073,1.711,0.212),
    76: (1.877,1.729,0.239),
    77: (2.005,-0.028,0.204),
    78: (0.167,-0.042,0.226),
    86: (-0.078,1.498,0.213),
    95: (-0.066,0.106,0.199)
}

for marker in chunk.markers:
    idx = int(marker.label[-2:])
    if idx in marker_coordinates:
        coords = marker_coordinates[idx]
        print(coords)
        marker.reference.location = Metashape.Vector(coords)
        marker.reference.enabled = True  # Ensure the marker is enabled in the reference system
        print(f"Set marker {idx} with coordinates: {coords}")
    else:
        print(f"Marker {idx} not found in reference coordinates!")

# Log all marker coordinates for debugging
for marker in chunk.markers:
    if marker.reference.location is not None:
        print(f"Marker {marker.label} coordinates: {marker.reference.location}")

# Update transformation (optimize camera alignment and marker position)
chunk.updateTransform()

# Build depth maps (required before building point cloud)
chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)

# Build dense point cloud
chunk.buildPointCloud(source_data=Metashape.DepthMapsData, point_colors=True)

# Export the point cloud to a .ply file
chunk.exportPointCloud(point_cloud_path, format=Metashape.PointCloudFormatPLY)

# Save project after processing
doc.save()

print("Script completed successfully.")