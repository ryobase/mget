import setuptools
import os

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name="mget",
    version="0.1.0",
    url="",
    py_modules=['mget'],

    author="Moss Pakhapoca",
    author_email="thorsleepless@gmail.com",

    license="MIT",

    description="wget clone written in Python 3",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    # install_requires=["Click"],
    install_requires=install_requires,

    python_requires='>=3',
    
    entry_points="""
        [console_scripts]
        mget=mget.core:cli
    """,

    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
