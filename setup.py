import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("version = ['\"]([^'\"]+)['\"]", init_py).group(1)


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
    name='Elastic-APM-ASGI',
    version=get_version('elastic_apm_asgi'),
    url='https://github.com/Mdslino/Elastic-APM-ASGI',
    license='BSD',
    description='Elastic APM integration for ASGI frameworks.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Marcelo Lino',
    author_email='mdslino@gmail.com',
    packages=get_packages('elastic_apm_asgi'),
    install_requires=['elastic-apm', 'starlette'],
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
