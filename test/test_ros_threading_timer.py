""" Tests conforming with [pytest] framework requirements, for testing the 
    [ros_threading_timer] package.

[pytest]: https://docs.pytest.org
[ros_threading_timer]: https://github.com/ricmua/ros_threading_timer

Usage examples: 

`python3 -m pytest path/to/test`

`pytest test_package::test_module`

`pytest -k test_pattern path/to/test/root`

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

# Import fixtures.
from .fixtures import ros
from .fixtures import node
from .fixtures import Timer


# Test baseline conditions for the task node.
TOLERANCE_S = 0.001
@pytest.mark.parametrize("interval_s", [(0.005), (0.010), (0.050), (0.200)])
def test_timeout(Timer, interval_s):
    
    # Define a callback.
    def callback(*args, **kwargs): pass
    
    # Initialize a new timer.
    timer = Timer(function=callback, interval=interval_s)
    
    # Start the timer.
    timer.start()
    
    # Join the timer, to wait for the timeout.
    timer.join(timeout=interval_s + TOLERANCE_S)
    
    # Verify that the elapsed time is as expected.
    elapsed_s = timer._elapsed_ns / 1e9
    print(f'Expected: {interval_s}; Elapsed: {elapsed_s}')
    assert abs(elapsed_s - interval_s) <= TOLERANCE_S
    
    # Verify that the callback was invoked.
    assert timer._future.done()
    
  


