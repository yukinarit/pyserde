import pathlib
import re
import sys
from codecs import open
from setuptools import setup, find_packages

root = pathlib.Path(__file__).parent.absolute()

with open('serde/__init__.py', 'r', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

setup_requires = [
    'pytest-runner',
]

requires = [
    'msgpack',
    'toml',
    'pyyaml',
    'stringcase',
    'typing_inspect>=0.4.0',
    'jinja2',
]

# Installs dataclasses from PyPI for python < 3.7
if sys.version_info < (3, 7):
    requires.append('dataclasses')

tests_require = [
    'coverage',
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'mypy',
    'flake8',
]

setup(
    name='pyserde',
    version=version,
    description='Serialization library on top of dataclasses.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='yukinarit',
    author_email='yukinarit84@gmail.com',
    url='https://github.com/yukinarit/pyserde',
    packages=find_packages(exclude=['test_serde', 'bench']),
    python_requires=">=3.6",
    setup_requires=setup_requires,
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
