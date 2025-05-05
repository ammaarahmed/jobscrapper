from setuptools import setup, find_packages

setup(
    name="ai-jobsraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pyyaml",
        "pytest",
        "pytest-mock",
        "pytest-cov",
        "pytest-asyncio",
    ],
)