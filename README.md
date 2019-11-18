An example project implementing an OpenStack REST API proxy that modifies
the API responses before returns it to the client.

Usage
-----
Install and start the proxy server:
```shell script
$ git clone https://github.com/gibizer/openstack-rest-proxy-example.git
$ cd openstack-rest-proxy-example
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ proxy.py  --plugins openstack_rest_proxy.proxy.ResponseAdapterPlugin \
    --port 3128 --host 127.0.0.1
```

Configure the http_proxy env variable to direct your openstack CLI client to 
the proxy:
```shell script
$ export http_proxy=http://127.0.0.1:3128
```

Modifying API responses
-----------------------
The `proxy.ResponseAdapterPlugin` is configured via the `RESPONSE_ADAPTERS` 
list to call a list of adapters  inheriting from `adapters.ResponseAdapterBase`
for each API response before it is returned to the client. The adapters can 
change the status code, the  headers and the body of the response. The 
`adapters.RemovePasswordExpiresAt` is an example adapter that removes the 
`password_expires_at` key from various Keystone API responses. 