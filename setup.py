from setuptools import find_packages, setup

setup(
    name='Fang-CMS',
    version='1.0.3',
    description="A Blog CMS written in Flask.",
    author="Tyler Gautney",
    author_email="linuxdragon57@codedragon.dev",
    url="https://github.com/LinuxDragon57/Fang-CMS",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="AGPL",
    install_requires=[
        'click',
        'Flask',
        'Flask-SQLAlchemy',
        'gunicorn',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'mistune==2.0.2',
        'toml',
        'psycopg2-binary',
        'pycryptodomex',
        'pyotp',
        'python-dotenv',
        'pywarp',
        'segno',
        'sqlalchemy',
        'werkzeug'
    ],
)
