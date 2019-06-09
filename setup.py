from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="github-contents",
    description="Python class for reading and writing data to a GitHub repository",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/github-contents",
    license="Apache License, Version 2.0",
    version=VERSION,
    py_modules=["github_contents"],
    install_requires=["requests"],
    extras_require={"test": ["pytest", "betamax"]},
    tests_require=["github-contents[test]"],
)
