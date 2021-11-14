from setuptools import find_packages, setup

setup(
    name='dragon-blogger',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'mistune==2.0.0rc1',
        'toml',
        'python-dotenv'
    ],
)
