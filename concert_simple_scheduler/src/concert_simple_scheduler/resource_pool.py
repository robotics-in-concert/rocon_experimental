# Software License Agreement (BSD License)
#
# Copyright (C) 2013, Jack O'Quin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the author nor of other contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
.. module:: resource_pool

This module tracks all known resources managed by this scheduler.  The ROS
`scheduler_msgs/Resource`_ message describes resources used by the
`Robotics in Concert`_ (ROCON) project.

.. _ROCON: http://www.robotconcert.org/wiki/Main_Page
.. _`Robotics in Concert`: http://www.robotconcert.org/wiki/Main_Page
.. _`scheduler_msgs/KnownResources`:
    http://docs.ros.org/api/scheduler_msgs/html/msg/KnownResources.html

"""
import copy
import itertools

## ROS messages
from scheduler_msgs.msg import Resource
#from scheduler_msgs.msg import CurrentStatus, KnownResources
from rocon_scheduler_requests.resources import CurrentStatus, KnownResources

from rocon_scheduler_requests.resources import ResourceSet

# some resources for testing
TEST_RAPPS = set(('rocon_apps/teleop', 'example/rapp'))
MARVIN = CurrentStatus(
    platform_info='rocon:///linux/precise/ros/turtlebot/marvin',
    rapps=TEST_RAPPS)
ROBERTO = CurrentStatus(
    platform_info='rocon:///linux/precise/ros/turtlebot/roberto',
    rapps=TEST_RAPPS)
TEST_DATA = [MARVIN, ROBERTO]           # test resources


class ResourcePool:
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = TEST_DATA
        self.pool = ResourceSet(iterable)

    def allocate(self, request):
        """ Try to allocate all resources for a *request*.

        :param request: Scheduler request message, some resources may
            include regular expression syntax.  *Does not modify this
            request.*
        :type request: ``scheduler_msgs/Request``

        :returns: List of ``scheduler_msgs/Resource`` messages
            allocated, in requested order with platform info fully
            resolved; or ``[]`` if not everything is available.

        If successful, matching ROCON resources are allocated to this
        *request*.

        """
        # Make a list containing sets of the available resources
        # matching each requested item.
        matches = self.match_list(request.resources)
        if not matches:                 # unsuccessful?
            return []                   # give up

        # At least one resource is available that satisfies each item
        # requested.  Look for a permutation that satisfies them all.
        #
        # If the list is long, n! permutations will take too much
        # time.  TODO: Figure out a good heuristic to use with long
        # lists, maybe just trying them once in the original order.
        for perm in itertools.permutations(range(len(alloc))):
            alloc = self.allocate_permutation(perm, request.resources)
            if alloc:                   # successful?
                return alloc
        return []                       # failure

    def allocate_permutation(perm, resources):
        print(str(perm), + '\nresources:\n' + resources)
        return copy.deepcopy(resources)  # copy fake results

    def match_list(self, resources):
        """
        Make a list containing sets of the available resources
        matching each element of *resources*.

        :returns: List of :class:`.ResourceSet` containing matching
            resources, empty if any item cannot be satisfied.
        """
        matches = []
        for res_req in resources:
            match_set = self.match_subset(res_req)
            if len(match_set) == 0:     # no matches for this resource?
                return []               # give up
            matches.append(match_set)

    def match_subset(self, resource_request):
        """ Find all resources matching *resource_request*.

        :returns: :class:`.ResourceSet` containing matching resources.
        """
        avail = ResourceSet()
        for res in self.pool.resources.values():
            if (res.status == CurrentStatus.AVAILABLE
                    and res.match(resource_request)):
                avail.add(res)
        return avail

    def release(self, resources):
        """ Release all the *resources* in this list. """
        pass                            # stub, nothing released
