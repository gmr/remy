from setuptools import setup
from remy import __version__, __description__
import sys

requirements = ['lxml', 'requests', 'sh']

if sys.version_info < (2, 7, 0):
    requirements.append('argparse')

scripts = ['remy=remy.cli:main']

# Build the path to install the support files

setup(name='remy',
      version=__version__,
      author='Gavin M. Roy',
      author_email='gavinmroy@gmail.com',
      packages=['remy'],
      url='https://github.com/gmr/remy',
      summary=__description__,
      long_description=open('README.md').read(),
      install_requires=requirements,
      license=open('LICENSE').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities'],
      entry_points={'console_scripts': scripts},
      zip_safe=True)