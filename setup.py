from setuptools import setup

with open('README.rst') as readme_file:
    long_description = readme_file.read()

setup(
    name='centerpoints',
    version='0.1.0',
    description='Approximation Algorithms for Centerpoints',
    maintainer='',
    maintainer_email='',
    url='https://github.com/fu-berlin-swp-2014/center-points',
    packages=['centerpoints'],
    license='MIT',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'centerpoints = centerpoints.centerpoints:main',
        ]
    },
)
