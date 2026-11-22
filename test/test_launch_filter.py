"""Launch test: the installed ground_filter_node as its own process.

The test process publishes one synthetic cloud on /velodyne_points with points just inside
and just outside the pass-through limits (z from -0.3 to 5.0 m, sensor frame) and checks
exactly which points come back on /velodyne_filtered, and that the header is kept.
Run: launch_test test/test_launch_filter.py (after sourcing the workspace).
"""
import os
import time
import unittest

import launch
import launch_ros.actions
import launch_testing
import launch_testing.actions
import launch_testing.asserts
import pytest
import rclpy
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

KEPT_Z = [-0.29, 0.0, 1.0, 4.99]
DROPPED_Z = [-1.0, -0.31, 5.01, 8.0]


@pytest.mark.launch_test
def generate_test_description():
    node = launch_ros.actions.Node(
        package='perception_pipeline', executable='ground_filter_node', output='screen')
    return launch.LaunchDescription([node, launch_testing.actions.ReadyToTest()]), {'node': node}


class TestFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def test_pass_through_limits(self):
        probe = rclpy.create_node('filter_probe')
        got = []
        probe.create_subscription(PointCloud2, '/velodyne_filtered', got.append, 10)
        pub = probe.create_publisher(PointCloud2, '/velodyne_points', 10)
        header = Header(frame_id='velodyne')
        points = [(1.0, float(i), z) for i, z in enumerate(KEPT_Z + DROPPED_Z)]
        cloud = point_cloud2.create_cloud_xyz32(header, points)
        try:
            start = time.monotonic()
            while not got and time.monotonic() - start < 20.0:
                pub.publish(cloud)
                rclpy.spin_once(probe, timeout_sec=0.2)
        finally:
            probe.destroy_node()
        self.assertTrue(got, 'no /velodyne_filtered message within 20 s')
        out = got[-1]
        self.assertEqual(out.header.frame_id, 'velodyne')
        zs = sorted(round(float(p[0]), 2) for p in point_cloud2.read_points(out, field_names=('z',)))
        self.assertEqual(zs, sorted(KEPT_Z))
        path = os.environ.get('FILTER_CSV')  # optional, for scripts/plot_filter.py
        if path:
            with open(path, 'w') as f:
                f.write('z,returned\n')
                f.writelines(f'{z},{int(round(z, 2) in zs)}\n' for z in KEPT_Z + DROPPED_Z)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):

    def test_exit_code(self, proc_info, node):
        launch_testing.asserts.assertExitCodes(proc_info, process=node)
