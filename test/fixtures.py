""" Test [fixtures] for using the [pytest] framework to test the 
    [ros_threading_timer] package.

[pytest]: https://docs.pytest.org
[ros_threading_timer]: https://github.com/ricmua/ros_threading_timer
[fixtures]: https://docs.pytest.org/en/6.2.x/fixture.html

Examples
--------

>>> 

"""

# Copyright 2023 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import pytest.
import pytest

# Import ROS.
import rclpy
import rclpy.node
import rclpy.executors

# Import ros_threading_timer.
import ros_threading_timer


# Initialize a ROS2 interface.
@pytest.fixture(scope='module')
def ros():
    
    # Initialize.
    rclpy.init()
    
    # Yield the product.
    yield rclpy
    
    # Cleanup.
    rclpy.shutdown()
    
  

# Initialize a ROS2 node.
@pytest.fixture
def node(ros):
    
    # Initialize a ros_transitions node.
    node = rclpy.node.Node('test')
    
    # Yield the product.
    yield node
    
    # Cleanup.
    node.destroy_node()
    
  

# Initialize a single-threaded executor to accurately measure timing.
@pytest.fixture
def executor(node):
    
    # Initialize an executor.
    executor = rclpy.executors.SingleThreadedExecutor()
    
    # Add the node.
    executor.add_node(node)
    
    # Yield the product.
    yield executor
    
    # Cleanup.
    del executor
    
  

# Initialize a wrapped Timer callable.
@pytest.fixture
def Timer(node):
    
    # Initialize a ROS2 timer.
    ros_timer = node.create_timer(timer_period_sec=1, callback=lambda: None)
    
    # Cancel the timer.
    ros_timer.cancel()
    
    # Wrap the ROS2 timer with a threading-style timer class.
    Timer = ros_threading_timer.TimerWrapper(ros_timer, node=node)
    
    # Yield the product.
    yield Timer
    
    # Cleanup.
    del Timer
    
  

# __main__
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
  

