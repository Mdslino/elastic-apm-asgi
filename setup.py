import ast
import os
import re

from setuptools import setup


def get_version() -> str:
    version_file = open(os.path.join("elastic_apm_asgi", "version.py"), encoding="utf-8")
    for line in version_file:
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split(" = ")[1])
            return version
    return "unknown"


def get_long_description():
    """
    Return the README.
    """
    return open('README.md', 'r', encoding="utf8").read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name='elastic-apm-asgi',
    version=get_version(),
    url='https://github.com/Mdslino/Elastic-APM-ASGI',
    license='BSD',
    description='Elastic APM integration for ASGI frameworks.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Marcelo Lino',
    author_email='mdslino@gmail.com',
    packages=get_packages('elastic_apm_asgi'),
    install_requires=['elastic-apm'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
