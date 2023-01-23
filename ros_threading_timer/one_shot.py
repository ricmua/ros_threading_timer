""" Wrapper that mimics the interface of [ROS2 Timer] but acts as a one-shot 
    (i.e., non-repeating, non-periodic) timer.

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

Demonstrate that the ROS2 timer is periodic, before stopping the timer.

>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
Timeout
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
Timeout
>>> ros_timer.cancel()

Verify that the timer is deactivated.

>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)

Wrap the ROS2 timer with a one-shot timer class.

>>> from ros_threading_timer.one_shot import TimerWrapper
>>> Timer = TimerWrapper(ros_timer)

The Timer class expects the timeout period in nanoseconds, rather than seconds, 
like the `create_timer` function. Make the conversion.

>>> import rclpy.utilities
>>> timer_period_ns = rclpy.utilities.timeout_sec_to_nsec(timer_period_s)

Create a "new" timer.

>>> timer = Timer(callback=lambda: print('One-shot timeout'),
...               timer_period_ns=timer_period_ns)

Verify that the callback is called only once after the timer is activated.

>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
One-shot timeout
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
>>> timer.is_canceled()
True

Verify that the timer can be re-used.

>>> timer.reset()
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
One-shot timeout
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)

Verify that the timer does not cut short the timeout interval.

>>> timer.reset()
>>> rclpy.spin_once(node, timeout_sec=timer_period_s - tolerance_s)
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)
One-shot timeout

Verify that the timer can be invoked multiple times, with different parameters.

>>> timer = Timer(callback=lambda: print('One-shot timeout verification'),
...               timer_period_ns=round(timer_period_ns / 2))
>>> timer.time_until_next_call() > timer_period_s / 2 - tolerance_s
True
>>> rclpy.spin_once(node, timeout_sec=timer_period_s / 2 - tolerance_s)
>>> rclpy.spin_once(node, timeout_sec=timer_period_s / 2 + tolerance_s)
One-shot timeout verification
>>> tolerance_ns = rclpy.utilities.timeout_sec_to_nsec(tolerance_s)
>>> timer.time_since_last_call() < tolerance_ns
True
>>> rclpy.spin_once(node, timeout_sec=timer_period_s + tolerance_s)

Cleanup by destroying the node and shutting down the ROS2 interface.

>>> node.destroy_node()
>>> rclpy.shutdown()


References
----------

[ROS2 Timer]: https://docs.ros2.org/latest/api/rclpy/api/timers.html

[threading]: https://docs.python.org/3/library/threading.html

[threading_timer]: https://docs.python.org/3/library/threading.html#timer-objects

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


class TimerWrapper:
    """ A wrapper that converts a _periodic_ [ROS2 Timer] into a one-shot timer.
    
    Although this is a wrapper (and not e.g. a derived class), every effort is 
    made to preserve the [ROS2 Timer] interface.
    
    Arguments
    ---------
    ros_timer : [rclpy.timer.Timer]
        An initialized [ROS2 Timer].
    
    """
    def __init__(self, ros_timer):
        
        # Wrap an already-initialized ROS timer.
        self._timer = ros_timer
        
    def __call__(self, callback, 
                       timer_period_ns, 
                       *args,
                       callback_group=None, 
                       clock=None,
                       context=None):
        """ A [callable] entry point that replaces the [ROS2 Timer] constructor.
        
        Most of the arguments are ignored, for now, since it is assumed that 
        the ROS2 timer has already been initialized.
        
        Arguments
        ---------
        callback : callable
            Timer callback function.
        timer_period_ns : int
            Timer period in nanoseconds.
        """
        
        # Stop the timer.
        self._timer.cancel()
        
        # Set a new period and callback.
        self._timer.timer_period_ns = timer_period_ns
        self._timer.callback = self._callback_wrapper
        self._callback = callback
        self._args = args
        
        # Restart the timer.
        self._timer.reset()
        
        # Return Timer-like object.
        return self
        
    def cancel(self):
        """ Cancel the timer.
        
        According to [rcl/timer.h]:
        
        >  A canceled timer can be reset... and then used again. 
           Calling this function on an already canceled timer will succeed.
        """
        self._timer.cancel()
    
    def destroy(self):
        """ Destroy the timer. """
        self._timer.destroy()
    
    def is_canceled(self):
        """ Check whether or not the timer is canceled. """
        return self._timer.is_canceled()
    
    def is_ready(self):
        """ Check whether or not the timer is ready. """
        return self._timer.is_ready()
        
    def reset(self):
        """ Reset the timer.
        
        According to [rcl/timer.h]:
        
        >  This function can be called on a timer, canceled or not. 
           For all timers it will reset the last call time to now. 
           For canceled timers it will additionally make the timer not canceled.
        """
        self._timer.reset()
        
    def time_since_last_call(self):
        """ Return time since last call. """
        return self._timer.time_since_last_call()
        
    def time_until_next_call(self):
        """ Return time until next call. """
        return self._timer.time_until_next_call()
    
    #property clock
    
    #property handle
    
    #property timer_period_ns
    
    def _callback_wrapper(self, *args, **kwargs):
        """ A wrapper for the timer callback function that cancels the timer, 
            in order to implement the one-shot functionality.
        """
        args = [*self._args, *args]
        self.cancel()
        self._callback(*args, **kwargs)    


