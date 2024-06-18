from setuptools import setup, find_packages

setup(
    name='osuParseMpLinks',
    version='0.1.1',
    packages=find_packages(include=['osuParseMpLinks', 'osuParseMpLinks.*']),
    install_requires=[
        'Requests>=2.31.0'
    ]
)
