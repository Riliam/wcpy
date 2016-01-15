from setuptools import setup, find_packages

setup(
    name='wcpy',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'aiohttp',
        'aiozmq',
        'aioredis',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        wcpy=wcpy.cli:cli
    ''',
)
