---
title: README
author: a.whit ([email](mailto:nml@whit.contact))
date: September 2022
---

<!-- License

Copyright 2022 Neuromechatronics Lab, Carnegie Mellon University (a.whit)

Created by: a. whit. (nml@whit.contact)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->

# ROS2 threading timer

This package provides a wrapper that mimics the interface of the 
[Timer][threading_timer] class in the Python [threading] package, but 
implements the timer functionality using a provided [ROS2 Timer].

A secondary goal of this package is to gather documentation about ROS2 clocks 
and timers.

## Installation

This package should generally be checked-out and built as part of a 
[ROS2 workspace][ros2_workspace].

## Example

Perhaps the best way to introduce the package and task is via an example. This 
example is provided in [doctest] format, and can be run via the following 
code:[^properly_installed]

[^properly_installed]: Provided that the package is properly installed.

```python
import doctest
doctest.testfile('README.md', module_relative=False)

```

It is assumed that the [ROS2 environment][ros2_environment] and the 
[ROS2 overlay][ros2_overlay] have both been properly initialized, before 
running the example.

This example illustrates how the `ros_threading_timer` package can be used to 
treat a [ROS2 Timer] like a [threading.Timer]. It is assumed that an 
initialized [ROS2] node exists, and that we wish to plug a timer derived from 
it into code tat expects a [threading] style of interface. Initialize a ROS2 
interface, a ROS2 node, and a ROS2 timer.

```python
>>> import rclpy
>>> import rclpy.node
>>> rclpy.init()
>>> node = rclpy.node.Node('test')
>>> ros_timer = node.create_timer(timer_period_sec=1, 
...                               callback=lambda: None)

```

Define a timeout interval and a tolerance. For this example, we will use an 
interval of 20 milliseconds. The tolerance is the maximum amount of deviation 
from an expected interval that we will tolerate before raising an error. In 
general, this should be quite small. Here, we will use a tolerance of one 
millisecond.

```python
>>> timer_period_s = 0.020
>>> tolerance_s = 0.001

```

Wrap the ROS2 timer with a threading-style timer class, and create a new timer 
interface.

```python
>>> from ros_threading_timer import TimerWrapper
>>> Timer = TimerWrapper(ros_timer, node=node)
>>> timer = Timer(function=lambda: print('Timeout'),
...               interval=timer_period_s)
>>> timer.is_alive()
False

```

The callback is called once -- and only once -- after the timer is activated.

```python
>>> timer.start()
>>> timer.is_alive()
True
>>> timer.join(timeout=timer_period_s + tolerance_s)
Timeout
>>> timer.is_alive()
False
>>> timer.join(timeout=timer_period_s + tolerance_s) # No callback.

```

As required by the [threading] package, the timer cannot be started a second 
time.

```python
>>> try: timer.start()
... except RuntimeError as e: print(e)
Timer has already been started.

```

A new timer can easily be created and run.

```python
>>> timer = Timer(function=lambda: print('New timeout'),
...               interval=timer_period_s)
>>> timer.start()
>>> timer.join(timeout=timer_period_s + tolerance_s)
New timeout

```

The callback will not be called for a timer that is cancelled before the 
timeout interval expires.

```python
>>> timer = Timer(function=lambda: print('Timeout'),
...               interval=timer_period_s)
>>> timer.start()
>>> timer.join(timeout=round(timer_period_s / 2))
>>> timer.cancel()
>>> timer.is_alive()
False

```

Once cancelled, a timer cannot be restarted. A new timer must be created.

```python
>>> try: timer.start()
... except RuntimeError as e: print(e)
Timer has already been started.

```

Cleanup by destroying the node and shutting down the ROS2 interface.

```python
>>> node.destroy_node()
>>> rclpy.shutdown()

```

## One-shot timer

This package also contains an implementation of a wrapper that mimics the 
interface of [ROS2 Timer] but acts as a one-shot (i.e., non-repeating, 
non-periodic) timer.
See [one_shot.py](ros_threading_timer/one_shot.py) for further information and 
documentation.


## Relevant links

* [rclcpp::TimerBase]
* [threading.Thread]
* [threading.Timer]
* [rcl/timer.h]

## License

Copyright 2022 [Neuromechatronics Lab][neuromechatronics], 
Carnegie Mellon University

Created by: a. whit. (nml@whit.contact)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

<!---------------------------------------------------------------------
   References
---------------------------------------------------------------------->

[ROS2]: https://docs.ros.org/en/humble/index.html

[threading]: https://docs.python.org/3/library/threading.html

[threading_timer]: https://docs.python.org/3/library/threading.html#timer-objects

[threading_thread]: https://docs.python.org/3/library/threading.html#threading.Thread

[ros2_workspace]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html

[ros2_environment]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html#source-ros-2-environment

[ros2_overlay]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html#source-the-overlay

[doctest]: https://docs.python.org/3/library/doctest.html

[ROS2 Timer]: https://docs.ros2.org/latest/api/rclpy/api/timers.html

[threading]: https://docs.python.org/3/library/threading.html

[threading_timer]: https://docs.python.org/3/library/threading.html#timer-objects

[rclpy.timer.Timer]: https://docs.ros2.org/latest/api/rclpy/api/timers.html#rclpy.timer.Timer 

[rclcpp::TimerBase]: https://docs.ros2.org/latest/api/rclcpp/classrclcpp_1_1TimerBase.html

[callable]: https://docs.python.org/3/reference/datamodel.html#object.__call__

[rcl/timer.h]: https://docs.ros2.org/beta3/api/rcl/timer_8h.html

[threading.Timer]: https://docs.python.org/3/library/threading.html#timer-objects

[threading.Thread]: https://docs.python.org/3/library/threading.html#threading.Thread

