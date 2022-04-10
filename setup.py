from setuptools import find_packages, setup

setup(
    name='LinuxDragon_CMS',
    version='0.0.1',
    description="A Blog CMS",
    author="E. L. Jackson",
    author_email="linuxdragon57@codedragon.dev",
    url="https://github.com/LinuxDragon57/linuxdragon_cms",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="AGPL",
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'mistune==2.0.0rc1',
        'toml',
        'python-dotenv',
        'segno',
        'pyotp',
        'pywarp',
        'pycryptodomex'
    ],
)
