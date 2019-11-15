#
# Copyright 2014 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""
Defines exceptions that are thrown by the Google Maps client.
"""

class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return str(self.status)
        else:
            return "%s (%s)" % (self.status, self.message)

class TransportError(Exception):
    """Something went wrong while trying to execute the request."""

    def __init__(self, base_exception=None):
        self.base_exception = base_exception

    def __str__(self):
        if self.base_exception:
            return str(self.base_exception)

        return "An unknown error occurred."

class HTTPError(TransportError):
    """An unexpected HTTP error occurred."""
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "HTTP Error: %d" % self.status_code

class Timeout(Exception):
    """The request timed out."""
    pass

class _RetriableRequest(Exception):
    """Signifies that the request can be retried."""
    pass

class _OverQueryLimit(ApiError, _RetriableRequest):
    """Signifies that the request failed because the client exceeded its query rate limit.

    Normally we treat this as a retriable condition, but we allow the calling code to specify that these requests should
    not be retried.
    """
    pass
