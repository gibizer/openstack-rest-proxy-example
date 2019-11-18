import json
import logging

import proxy

from openstack_rest_proxy import adapters

LOG = logging.getLogger(__name__)


class ResponseAdapterPlugin(proxy.HttpProxyBasePlugin):
    """Proxy plugin that converts OpenStack API responses
    """

    # Response adapters are executed in the define order. The adapters are
    # chained so the next adapter always works on the output of the previous
    # adapter
    RESPONSE_ADAPTERS = [adapters.RemovePasswordExpiresAt()]

    def before_upstream_connection(self):
        return False

    def on_upstream_connection(self):
        pass

    def handle_upstream_response(self, raw):
        rsp = proxy.HttpParser(proxy.HttpParserTypes.RESPONSE_PARSER)
        rsp.parse(raw)

        if rsp.body is not None:
            try:
                json_body = json.loads(rsp.body)
                json_body = self._apply_adapters(rsp, json_body)
                rsp.body = json.dumps(json_body).encode("utf-8")
            except json.JSONDecodeError:
                # Adapters only support responses with json body at the moment
                # other responses transparently returned
                pass

        return proxy.build_http_response(
            status_code=int(rsp.code),
            headers={
                rsp.headers[k][0]: rsp.headers[k][1] for k in rsp.headers
            },
            body=rsp.body,
        )

    def on_upstream_connection_close(self):
        pass

    def _apply_adapters(self, rsp, json_body):
        code = rsp.code
        headers = rsp.headers
        for adapter in self.RESPONSE_ADAPTERS:
            code, headers, json_body = adapter.adapt(
                self.request.method,
                self.request.url,
                self.request.headers,
                code,
                headers,
                json_body,
            )
        rsp.code = code
        rsp.headers = headers
        return json_body
