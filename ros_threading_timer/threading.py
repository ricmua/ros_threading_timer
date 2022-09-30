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

>>> from ros_threading_timer.threading import TimerWrapper
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

# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import ROS2 packages and modules.
import rclpy.utilities

# Import local modules.
from . import one_shot


# Define the wrapper.
class TimerWrapper(one_shot.TimerWrapper):
    """ A wrapper that provides a [threading Timer][threading_timer]-like 
        interface for a [ROS2 Timer].
    
    Arguments
    ---------
    *args : list
        Arguments. See `one_shot.TimerWrapper`.
    node : rclpy.node.Node
        A ROS2 node to associate with the timer. This argument is optionally, 
        but the `join` method will fail if a valid node is not provided.
    *kwargs : list
        Keyword arguments. See `one_shot.TimerWrapper`.
    """
    def __init__(self, *args, node=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._node = node
        
    def __call__(self, interval, function, args=None, kwargs=None):
        """ A [callable] entry point that overrides 
            `one_shot.TimerWrapper.__call__`, and replaces the 
            [threading Timer][threading_timer] constructor.
        
        Arguments
        ---------
        interval : float
            Timeout interval in seconds.
        function : callable
            Timer callback function.
        """
        
        # Set the initial state.
        self._started = False
        self._alive = False
        
        # Initialize defaults.
        args = args if not (args == None) else []
        kwargs = kwargs if not (kwargs == None) else {}
        
        # Invoke the superclass callable.
        timer_period_ns = rclpy.utilities.timeout_sec_to_nsec(interval)
        timer = super().__call__(*args, 
                                 callback=function, 
                                 timer_period_ns=timer_period_ns,
                                 **kwargs)
        
        # The threading constructor does not start the timer automatically.
        timer.cancel()
        
        # Return the result.
        return timer
        
    def start(self):
        """ Start the timer process.
        
        See the [threading.Thread].start method. This may only be called once 
        per thread.
        """
        
        # If the thread has already started, raise an exception.
        if self._started: raise RuntimeError('Timer has already been started.')
        
        # Start the timer.
        self._started = True
        self.run()
        self._alive = True
    
    def run(self):
        """ Run the timer.
        
        See the [threading.Thread].run method.
        """
        self.reset()
    
    def join(self, timeout=None):
        """ Wait until the timer terminates. 
        
        See the [threading.Thread].join method.
        
        Arguments
        ---------
        timeout : float
            Timeout for the blocking operation, in seconds.
        """
        
        # Ensure that the timer has been started.
        if not self._started:
            raise RuntimeError('Cannot join timer that has not been started.')
        
        # Ensure that the timer is alive.
        if not self._alive and not timeout:
            message = 'Cannot join timer that is not alive without a timeout'
            raise RuntimeError(message)
        
        # Record the start time.
        clock = self._node.get_clock()
        time_0 = clock.now()
        
        # Join by spinning.
        # Terminate the loop if the timer expires, or if the timeout expires.
        timeout = 1e9 if (timeout == None) else timeout
        while (timeout > 0) and self.is_alive():
            rclpy.spin_once(self._node, timeout_sec=timeout)
            elapsed_ns = (clock.now() - time_0).nanoseconds
            elapsed_s = elapsed_ns / 1e9
            timeout  -= elapsed_s
        
        # Always return None.
        return None
        
    def is_alive(self):
        """ Return whether the timer is alive.
        
        See the [threading.Thread].is_alive method.
        """
        return self._alive
        
    # property name
    
    # property ident
    
    # property native_id
    
    # property daemon
    
    def cancel(self):
        """ Overrides the cancel function to mark the timer no longer alive. """
        super().cancel()
        self._alive = False
        
    def _callback_wrapper(self, *args, **kwargs):
        """ Overrides the callback wrapper for the parent class in order to 
            update timer status.
        """
        super()._callback_wrapper(*args, **kwargs)
        self._alive = False 
    
  

