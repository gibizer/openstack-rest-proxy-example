from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="openstack-rest-proxy-example",
    version="0.1",
    description="OpenStack REST API proxy example",
    url="",
    author="Balazs Gibizer",
    author_email="gibizer@gmail.com",
    license="Apache License 2.0",
    packages=["openstack_rest_proxy"],
    zip_safe=False,
    install_requires=requirements,
)
