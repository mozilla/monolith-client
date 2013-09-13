import os
from setuptools import setup, find_packages

__version__ = '0.8'

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'requests',
    'statsd'
]

test_requires = requires + [
    'coverage',
    'mock',
    'monolith.web',
    'nose',
    'pyelasticsearch',
    'pyelastictest',
    'WebTest',
]

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()


classifiers = ["License :: OSI Approved :: Apache Software License",
               "Programming Language :: Python",
               "Programming Language :: Python :: 2",
               "Programming Language :: Python :: 2.6",
               "Programming Language :: Python :: 2.7",
               "Programming Language :: Python :: Implementation :: CPython",
               "Framework :: Pyramid",
               "Topic :: Internet :: WWW/HTTP",
               "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"]


setup(name='monolith.client',
      version=__version__,
      description='Mozilla Monolith Client',
      long_description=README + '\n\n' + CHANGES,
      classifiers=classifiers,
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.org',
      url='https://github.com/mozilla/monolith-client',
      license="Apache 2.0",
      packages=find_packages(),
      namespace_packages=['monolith'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      test_suite="monolith.client",
      extras_require={'test': test_requires})
