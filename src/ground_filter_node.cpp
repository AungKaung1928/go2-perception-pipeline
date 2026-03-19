#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/passthrough.h>

class GroundFilterNode : public rclcpp::Node
{
public:
  GroundFilterNode() : Node("ground_filter_node")
  {
    sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      "/velodyne_points", 10,
      std::bind(&GroundFilterNode::callback, this, std::placeholders::_1));

    pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
      "/velodyne_filtered", 10);

    RCLCPP_INFO(this->get_logger(), "Ground filter node started");
  }

private:
  void callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
  {
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::fromROSMsg(*msg, *cloud);

    pcl::PassThrough<pcl::PointXYZ> pass;
    pass.setInputCloud(cloud);
    pass.setFilterFieldName("z");
    pass.setFilterLimits(-0.3, 5.0);

    pcl::PointCloud<pcl::PointXYZ>::Ptr filtered(new pcl::PointCloud<pcl::PointXYZ>);
    pass.filter(*filtered);

    sensor_msgs::msg::PointCloud2 output;
    pcl::toROSMsg(*filtered, output);
    output.header = msg->header;
    pub_->publish(output);

    RCLCPP_INFO(this->get_logger(), "Input: %zu pts -> Filtered: %zu pts",
      cloud->size(), filtered->size());
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GroundFilterNode>());
  rclcpp::shutdown();
  return 0;
}
