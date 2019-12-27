import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'loco_sound', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open(os.path.join(here, 'requirements.txt'), 'r') as f:
    requirements = f.read().splitlines()

with open(os.path.join(here, 'requirements-dev.txt'), 'r') as f:
    requirements_dev = f.read().splitlines()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    url=about['__url__'],
    python_requires=">=3.6",
    install_requires=requirements,
    license=about['__license__'],
    tests_require=requirements_dev,
)
