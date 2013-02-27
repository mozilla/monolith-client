import os
from setuptools import setup, find_packages

__version__ = '0.1'

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'requests',
    'pyelasticsearch',
]

test_requires = requires + [
    'coverage',
    'monolith.web',
    'nose',
    'unittest2',
]

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='monolith.client',
    version=__version__,
    description='Monolith client',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    keywords="web services",
    author='Mozilla Services',
    author_email='services-dev@mozilla.org',
    url='https://github.com/mozilla/monolith-client',
    packages=find_packages(),
    namespace_packages=['monolith'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=test_requires,
    test_suite="monolith.client",
    extras_require={'test': test_requires},
)
