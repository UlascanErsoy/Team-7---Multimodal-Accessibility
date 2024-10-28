"""
This file contains the code for the projection of the data onto the audio (HRTF) space.
""" 

import numpy as np
import matplotlib.pyplot as plt
from xml.dom import minidom

def extract_svg_vectors(svg_path, origin=None):
    """
    Extract vectors from SVG file relative to a specified origin point.
    """
    # Parse SVG file
    doc = minidom.parse(svg_path)
    
    # Get all use elements inside PathCollection group
    svg_points = []
    path_collection = doc.getElementsByTagName('g')
    for g in path_collection:
        if g.getAttribute('id') == 'PathCollection_1':
            # Find the group with clip-path
            for group in g.getElementsByTagName('g'):
                if group.getAttribute('clip-path'):
                    # Get all use elements which contain our scatter points
                    uses = group.getElementsByTagName('use')
                    for use in uses:
                        x = float(use.getAttribute('x'))
                        y = float(use.getAttribute('y'))
                        svg_points.append((x, y))
    
    svg_points = np.array(svg_points)

    print("SVG Points:", svg_points)
    
    # Get SVG dimensions
    svg_element = doc.getElementsByTagName('svg')[0]
    viewBox = svg_element.getAttribute('viewBox').split()
    width = float(viewBox[2])
    height = float(viewBox[3])
    
    # Calculate center of SVG viewBox if origin not specified
    if origin is None:
        origin = np.array([width/2, height/2])
    else:
        origin = np.array(origin)
        
    # Calculate vectors relative to origin
    if len(svg_points) > 0:
        vectors = svg_points - origin
    else:
        vectors = np.array([])
        
    doc.unlink()
    return vectors, origin

# Polor Coordinates 
def calculate_polar_coordinates(vectors, d=1.0):
    """
    Calculate polar coordinates (r, theta, phi) from SVG vectors.
    
    SVG coordinate system:
    - Origin at center of SVG
    - +x points right 
    - +y points down
    - +z points out of screen (d parameter)
    
    Returns:
    - r: distance from origin to point
    - theta: azimuthal angle in x-y plane (0° at +x, increases CCW)
    - phi: polar angle from +z axis
    """
    # Add z coordinate (d) to make 3D points
    points_3d = np.column_stack((vectors, np.full(len(vectors), d)))
    
    # Calculate r (distance from origin to point)
    r = np.sqrt(np.sum(points_3d**2, axis=1))
    
    # Calculate theta (azimuthal angle in x-y plane)
    theta = np.degrees(np.arctan2(points_3d[:, 1], points_3d[:, 0]))
    # Convert to 0-360° range
    theta = (theta + 360) % 360
    
    # Calculate phi (polar angle from +z axis)
    phi = np.degrees(np.arccos(d / r))
    
    return np.column_stack((r, theta, phi))

if __name__ == "__main__":
    # Main execution
    np.random.seed(42)
    x = np.random.rand(10) * 10
    y = np.random.rand(10) * 10

    # Create scatter plot
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, color='blue')
    plt.grid(True)
    plt.axis('equal')

    # Save as SVG
    plt.savefig("scatter.svg", format="svg")
    plt.close()

    # Extract and print vectors
    vectors, origin = extract_svg_vectors('scatter.svg')
    print("\nVectors:", vectors)
    print("\nOrigin point:", origin)

    polar_coords = calculate_polar_coordinates(vectors)
    print("\nPolar Coordinates:", polar_coords)