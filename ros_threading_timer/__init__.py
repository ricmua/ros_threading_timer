""" Wrapper for a [ROS2 Timer] that mimics the interface of 
    the [Timer][threading_timer] class of the Python [threading] package.

Also see [rclcpp::TimerBase].


Examples
--------

Define a timer period for this example.

>>> timer_period_s = 0.050

Define a tolerance allowed for timing jitter. This should be a fraction of the 
timer period. Ideally, it will be less than a millisecond.

>>> tolerance_s = 0.001

Create a ROS2 node and retrieve a ROS2 timer.

>>> import rclpy
>>> import rclpy.node
>>> rclpy.init()
>>> node = rclpy.node.Node('test')
>>> ros_timer = node.create_timer(timer_period_sec=timer_period_s, 
...                               callback=lambda: print('Timeout'))

Wrap the ROS2 timer with a threading-style timer class.

>>> from ros_threading_timer import TimerWrapper
>>> Timer = TimerWrapper(ros_timer, node=node)

Create a "new" timer.

>>> timer = Timer(function=lambda: print('Threading-style timeout'),
...               interval=timer_period_s)
>>> timer.is_alive()
False

Verify that the callback is called only once after the timer is activated.

>>> timer.start()
>>> timer.is_alive()
True
>>> timer.join(timeout=timer_period_s + tolerance_s)
Threading-style timeout
>>> timer.is_alive()
False

Verify that the timer cannot be started a second time.

>>> try: timer.start()
... except RuntimeError as e: print(e)
Timer has already been started.

Verify that a new timer can be created and run.

>>> timer = Timer(function=lambda: print('New timer timeout'),
...               interval=timer_period_s)
>>> timer.start()
>>> timer.join(timeout=timer_period_s + tolerance_s)
New timer timeout

Start a new timer, wait half of the timeout interval, and then cancel it. The 
callback is not invoked.

>>> timer = Timer(function=lambda: print('New timeout'),
...               interval=timer_period_s)
>>> timer.start()
>>> timer.join(timeout=round(timer_period_s / 2))
>>> timer.cancel()
>>> timer.is_alive()
False
>>> try: timer.start()
... except RuntimeError as e: print(e)
Timer has already been started.

Verify that the timer interval is of the expected duration.

>>> class TimingTimerWrapper(TimerWrapper):
...     def start(self):
...         self._start_time = self._node.get_clock().now()
...         super().start()
...     def _callback_wrapper(self, *args, **kwargs):
...         self._callback_time = self._node.get_clock().now()
...         super()._callback_wrapper(*args, **kwargs)
>>> TimingTimer = TimingTimerWrapper(ros_timer,  node=node)
>>> timer = TimingTimer(function=lambda: print('Timed timeout'),
...                     interval=timer_period_s)
>>> timer.start()
>>> timer.join(timeout=timer_period_s + tolerance_s)
Timed timeout
>>> elapsed_ns = (timer._callback_time - timer._start_time).nanoseconds
>>> abs(elapsed_ns / 1e9 - timer_period_s) < tolerance_s
True

Cleanup by destroying the node and shutting down the ROS2 interface.

>>> node.destroy_node()
>>> rclpy.shutdown()


References
----------

[ROS2 Timer]: https://docs.ros2.org/latest/api/rclpy/api/timers.html

[threading]: https://docs.python.org/3/library/threading.html

[threading_timer]: https://docs.python.org/3/library/threading.html#timer-objects

[threading_thread]: https://docs.python.org/3/library/threading.html#threading.Thread

[rclpy.timer.Timer]: https://docs.ros2.org/latest/api/rclpy/api/timers.html#rclpy.timer.Timer 

[rclcpp::TimerBase]: https://docs.ros2.org/latest/api/rclcpp/classrclcpp_1_1TimerBase.html

[callable]: https://docs.python.org/3/reference/datamodel.html#object.__call__

[rcl/timer.h]: https://docs.ros2.org/beta3/api/rcl/timer_8h.html

"""

# Copyright 2022-2023 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import local modules.
from .threading import TimerWrapper


