from setuptools import setup

with open('README.rst') as readme_file:
    long_description = readme_file.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name='centerpoints',
    version='0.1.0',
    description='Approximation Algorithms for Centerpoints',
    maintainer='',
    maintainer_email='',
    url='https://github.com/fu-berlin-swp-2014/center-points',
    packages=['centerpoints'],
    license='MIT',
    install_requires=REQUIREMENTS,
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'centerpoints = centerpoints.cli:main',
        ],
        'gui_scripts': [
            'centerpoints-gui = centerpoints.visualise:run_gui',
        ]
    },
)
