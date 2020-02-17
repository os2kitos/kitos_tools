from setuptools import setup

setup(
    name="kitos_tools",
    version="0.0.1",
    description="A set of tools for working with KITOS data import and export",
    author="Anders Sølbech Larsen",
    author_email="asl@holstebro.dk",
    license="MPL 2.0",
    packages=[
        "kitos_helper",
    ],
    zip_safe=False,
    install_requires=[
        "requests",
    ]
)
