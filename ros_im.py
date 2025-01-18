import os
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Header

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.publisher = self.create_publisher(Image, '/image_raw', 10)
        self.bridge = CvBridge()
        self.timer = self.create_timer(1.0, self.timer_callback)  # publish every 1 second
        self.image_path = '/path/to/your/image.png'  # Path to your PNG image

    def timer_callback(self):
        # Read the PNG image using OpenCV (converts to NumPy array)
        cv_image = cv2.imread(self.image_path)

        if cv_image is not None:
            # Convert the NumPy array (OpenCV image) to a ROS image message
            ros_image = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            ros_image.header = Header()
            ros_image.header.stamp = self.get_clock().now().to_msg()
            ros_image.header.frame_id = "camera"
            
            # Publish the image
            self.publisher.publish(ros_image)
            self.get_logger().info(f'Publishing image: {self.image_path}')
        else:
            self.get_logger().error(f'Failed to load image: {self.image_path}')

def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
