from setuptools import setup, find_packages

setup(
    name="fastapi_test",
    version="0.1",
    packages=find_packages(),  # 自动发现 services, utils 等
)