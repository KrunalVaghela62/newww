# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YywAl2y89_aUZtY9iDudLqUa0BTP4org
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray  # Message type for the center points
from geometry_msgs.msg import Point  # Message type for 3D world coordinates (X, Y, Z)
import numpy as np

def pixel_to_world(u, v, depth, K):
    # Inverse of the intrinsic matrix
    inv_K = np.linalg.inv(K)

    # Convert pixel to normalized camera coordinates
    pixel_coords = np.array([u, v, 1])  # Homogeneous image coordinates
    normalized_coords = inv_K @ pixel_coords  # Apply inverse intrinsic matrix

    # Scale normalized coordinates by depth to get camera coordinates
    camera_coords = normalized_coords * depth  # [X_c, Y_c, Z_c]

    # Extract world coordinates
    X_w, Y_w, Z_w = camera_coords[:3]
    return X_w, Y_w, Z_w


class CenterSubscriber(Node):
    def __init__(self):
        super().__init__('center_subscriber')

        # Subscribe to the /u_v topic where the centers are being published
        self.subscription = self.create_subscription(
            Float32MultiArray,  # Message type for the center points
            '/u_v',  # Topic name (to match the publisher topic)
            self.listener_callback,  # Callback function to process the data
            10  # QoS (Quality of Service) policy
        )

        # Publisher to send the computed world coordinates to /motion_p topic
        self.motion_publisher = self.create_publisher(
            Point,  # The message type for the 3D world coordinates
            '/motion_p',  # The topic where world coordinates will be published
            10
        )

        # Example intrinsic camera matrix K
        self.K = np.array([
            [667.248390, 0.000000 ,644.165204],
            [0.000000 ,668.783677, 417.422792],
            [0.000000 ,0.000000 ,1.000000]
        ])

    def listener_callback(self, msg):
        # Extract center points (flattened array)
        centers = np.array(msg.data).reshape(-1, 2)

        # Assuming random depths for example (replace with real depth data if available)
        depths = np.random.rand(len(centers), 1) * 10  # Random depths between 0 and 10 meters

        # Process each center and compute world coordinates
        for (u, v), depth in zip(centers, depths):
            X_w, Y_w, Z_w = pixel_to_world(u, v, depth, self.K)

            # Log the world coordinates
            self.get_logger().info(f"World Coordinates: X={X_w}, Y={Y_w}, Z={Z_w}")

            # Create a Point message to publish the world coordinates
            world_point = Point()
            world_point.x = X_w
            world_point.y = Y_w
            world_point.z = Z_w

            # Publish the world coordinates to the /motion_p topic
            self.motion_publisher.publish(world_point)
            self.get_logger().info(f"Published world point: {world_point}")

def main(args=None):
    rclpy.init(args=args)
    center_subscriber = CenterSubscriber()

    rclpy.spin(center_subscriber)

    # Clean up
    center_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()