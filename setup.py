from os.path import abspath, dirname, exists, join
from setuptools import setup

install_reqs = [
    req for req in open(abspath(join(dirname(__file__), "requirements.txt")))
]

setup(
    name="dashpssh",
    author="Micael Silva",
    version="1.0.0",
    license="APACHE",
    zip_safe=False,
    include_package_data=True,
    install_requires=install_reqs,
    packages=["m3u8"],
    url="https://github.com/micaelsilva/dashpssh",
    description="PSSH parser for DASH manifestsr",
    python_requires=">=3.7",
)