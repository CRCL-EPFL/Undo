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
        if is_far_from(color, black_color, black_color_threshold) and points[i, 2] > 0.0:
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
image_folder = FOLDER + "/images"  # Change this to your image folder
project_path = FOLDER + "/metashape/model.psx"    # Path to save the Metashape project file
point_cloud_path = FOLDER + "/ply/model.ply"  # Path to export the point cloud as a .ply file

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
    11: (5.170,3.279,-0.197),
    14: (0.001,3.048,-0.192),
    16: (0.241,-0.004,-0.193),
    20: (0.187,3.285,-0.198),
    28: (5.392,0.226,-0.202),
    33: (5.397,3.093,-0.204),
    52: (5.223,-0.010,-0.191),
    53: (-0.000,0.168,-0.177),
    61: (5.146,3.060,-0.020),
    84: (0.172,3.055,-0.024),
    90: (0.174,0.181,-0.014),
    92: (0.205,1.726,-0.017),
    93: (3.429,3.047,-0.032)
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