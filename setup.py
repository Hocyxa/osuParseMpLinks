from setuptools import setup, find_packages

setup(
    name='osuParseMpLinks',
    version='0.1.3',
    packages=find_packages(include=['osuParseMpLinks', 'osuParseMpLinks.*']),
    install_requires=[
        'Requests>=2.31.0'
    ],
    include_package_data=True
)
