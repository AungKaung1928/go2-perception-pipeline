cmake_minimum_required(VERSION 3.8)
project(perception_pipeline)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(pcl_ros REQUIRED)
find_package(pcl_conversions REQUIRED)

add_executable(ground_filter_node src/ground_filter_node.cpp)
ament_target_dependencies(ground_filter_node
  rclcpp sensor_msgs pcl_ros pcl_conversions)

install(TARGETS ground_filter_node
  DESTINATION lib/${PROJECT_NAME})

ament_package()
