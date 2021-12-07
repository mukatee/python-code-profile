__author__ = 'teemu kanstren'

import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(name="codeprofile",
      version="1.0.2",
      description="Profiling CPU usage for blocks of code",
      description_content_type="text/markdown",
      long_description=README,
      long_description_content_type="text/markdown",
      url="https://github.com/mukatee/python-code-profile",
      author = 'Teemu Kanstrén',
      author_email = 'tkanstren@protonmail.com',
      license='MIT',
      packages=['codeprofile'],
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Development Status :: 5 - Production/Stable',
                   'Topic :: Software Development :: Testing',
                   'Topic :: Software Development',
                   ],
      keywords = ["profiling", "monitoring", "performance", "trace"],
      zip_safe=True,
      )
