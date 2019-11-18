import logging
import re
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from urllib import parse as urlparse

LOG = logging.getLogger(__name__)


class ResponseAdapterBase(object):
    """Base class for API response adapters. The adapt() method is called for
    each API response before it is sent back to the client.

    """

    def adapt(
        self,
        request_method: bytes,
        request_url: urlparse.SplitResultBytes,
        request_headers: Dict[bytes, Tuple[bytes, bytes]],
        response_code: bytes,
        response_headers: Dict[bytes, Tuple[bytes, bytes]],
        response_body: Union[Dict, List],
    ) -> (bytes, Dict[bytes, Tuple[bytes, bytes]], Union[Dict, List]):
        """Modify the API response before it sent back to the client.

        :param request_method: The HTTP method
        :param request_url: The HTTP request url
        :param request_headers: The HTTP headers in the request. The dict is
            keyed by the lower case header name the value is a tuple of
            (original-header-name, header-value)
        :param response_code:  The HTTP status code in the upstream response
        :param response_headers: The HTTP headers in the upstream response
        :param response_body:  The json body, e.g. python list or dict, in the
            upstream response
        :return: A triplet of the optionally modified (response_code,
            response_headers, response_body)
        """
        return response_code, response_headers, response_body


class RemovePasswordExpiresAt(ResponseAdapterBase):
    """Removed the password_expires_at from the keystone API responses
    """

    def adapt(
        self,
        request_method,
        request_url,
        request_headers,
        response_code,
        response_headers,
        response_body,
    ):
        modified = False
        # error response does not have user like data to drop
        # password_expires_at key form
        if int(response_code) >= 400:
            return response_code, response_headers, response_body

        # GET /v3/users
        if (
            b"/identity/v3/users" == request_url.path
            and request_method == b"GET"
        ):
            for user in response_body["users"]:
                modified = True
                user.pop("password_expires_at")

        # GET /v3/groups/{group_id}/users
        if (
            re.search(rb"/v3/groups/[^/]+/users", request_url.path)
            and request_method == b"GET"
        ):
            for user in response_body["users"]:
                modified = True
                user.pop("password_expires_at")

        # GET /v3/users/{user_id}
        # PATCH /v3/users/{user_id}
        if re.search(
            rb"v3/users/[^/]+", request_url.path
        ) and request_method in [b"GET", b"PATCH"]:
            modified = True
            response_body["user"].pop("password_expires_at")

        # POST /v3/users
        if (
            b"/identity/v3/users" == request_url.path
            and request_method == b"POST"
        ):
            modified = True
            response_body["user"].pop("password_expires_at")

        if modified:
            LOG.info(
                "The password_expires_at key is removed from the response "
                "of %s %s"
                % (request_method.decode(), request_url.path.decode())
            )

        return response_code, response_headers, response_body
