#!/usr/bin/python3
import os
import setuptools
import setuptools.command.build_py

setuptools.setup(
    name='WiFinder',
    version='1.0',
    description='Foxhunt an access point',
    keywords='wifi',
    author='Brian Murphy',
    url='https://github.com/gurudvlp/WiFinder',
    python_requires='>=3.8',
    install_requires=[
        ''
    ],
    include_package_data=True,
    data_files=[
        ('/usr/share/icons/hicolor/scalable/apps', ['wifinder/assets/wifinder.png']),
        ('/usr/share/applications', ['wifinder/assets/wifinder.desktop'])
    ],
    package_data={
        "": ["assets/*"]
    },
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'wifinder=wifinder',
        ],
    },
)
