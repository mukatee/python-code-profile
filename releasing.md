note to future self: how to make a release

https://realpython.com/pypi-publish-python-package/

- rm -rf dist
- python3 setup.py sdist bdist_wheel
- twine check dist/*
- twine upload dist/*