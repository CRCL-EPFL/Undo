import Metashape
import time
import numpy as np
import open3d as o3d
import math
import os

def is_far_from(color, against, threshold=50):
    # Calculate the Euclidean distance between the given color and the target color (black)
    distance = math.sqrt(
        (color[0] - against[0]) ** 2 +
        (color[1] - against[1]) ** 2 +
        (color[2] - against[2]) ** 2
    )
    # Check if the distance is within the threshold
    return distance >= threshold

def filter_point_cloud(input_path, output_path):
    # Read the point cloud
    pcd = o3d.io.read_point_cloud(input_path)

    # Convert to numpy array
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    # Define the color and threshold
    black_color = np.array([0, 0, 0])
    black_color_threshold = 1

    # Filter points and colors
    filtered_indices = []
    for i, color in enumerate(colors):
        if is_far_from(color, black_color, black_color_threshold) and points[i, 2] > 0.51:
            filtered_indices.append(i)

    filtered_indices = np.array(filtered_indices)
    filtered_points = points[filtered_indices]
    filtered_colors = colors[filtered_indices]

    # Create a new point cloud for the filtered data
    filtered_pcd = o3d.geometry.PointCloud()
    filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)
    filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_colors)

    # Remove outliers
    cl, ind = filtered_pcd.remove_statistical_outlier(nb_neighbors=100, std_ratio=2.0)
    inlier_pcd = filtered_pcd.select_by_index(ind)

    # Save the filtered point cloud
    o3d.io.write_point_cloud(output_path, inlier_pcd)

# Start timing the script
start_time = time.time()

HERE = os.path.dirname(__file__)
FOLDER = os.path.abspath(os.path.join(HERE, '..'))

# Define paths
<<<<<<< HEAD
image_folder = FOLDER + "/scan"  # Change this to your image folder
project_path = FOLDER + "/metashape/model.psx"    # Path to save the Metashape project file
point_cloud_path = FOLDER + "/ply/model.ply"  # Path to export the point cloud as a .ply file
=======
image_folder = "C:/Users/eleni/Desktop/scan/scan_state_C"  # Change this to your image folder
project_path = "K:/.shortcut-targets-by-id/1IiGhZQRuFujGaxqXg4taUaPR55vt4fB7/DMS 2024/06_RobotFiles/metashape/state_C.psx"   # Path to save the Metashape project file
point_cloud_path = "K:/.shortcut-targets-by-id/1IiGhZQRuFujGaxqXg4taUaPR55vt4fB7/DMS 2024/06_RobotFiles/metashape/automated_state_C.ply"  # Path to export the point cloud as a .ply file
>>>>>>> parent of 7869fa9 (test_scan)

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
        marker.reference.location = Metashape.Vector(coords)
        marker.reference.enabled = True  # Ensure the marker is enabled in the reference system
        print(f"Set marker {idx} with coordinates: {coords}")
    # else:
    #     print(f"Marker {idx} not found in reference coordinates!")

# Log all marker coordinates for debugging
# for marker in chunk.markers:
#     if marker.reference.location is not None:
#         print(f"Marker {marker.label} coordinates: {marker.reference.location}")

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

# End timing and print the elapsed time
end_time = time.time()
elapsed_time = (end_time - start_time)/60
print(f"Script took {elapsed_time:.2f} minutes to complete.")

input_ply_path = point_cloud_path  # Update with your .ply file path
output_ply_path = FOLDER + "/ply/model_clean.ply"  # Path to save the filtered .ply file

# Run the filter function
filter_point_cloud(input_ply_path, output_ply_path)