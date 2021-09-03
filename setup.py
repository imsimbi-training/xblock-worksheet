"""Setup for worksheet XBlock."""


import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='worksheet-xblock',
    version='1.1',
    description='Worksheet XBlock defined by HTML/CSS with multiple free text responses',
    license='Apache 2.0',
    packages=[
        'worksheet',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'worksheet = worksheet:WorksheetBlock',
        ]
    },
    package_data=package_data("worksheet", ["static", "public"]),
)
