import sys
from setuptools import setup, find_packages

install_requires = [
    'Click==6.7'
]

if sys.platform.startswith('win'):
    install_requires.extend([
        'colorama==0.3.3',
        'pyreadline==2.1'
    ])


setup(
    name='play',
    version='0.6.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        play=play:cli
    ''',
)
