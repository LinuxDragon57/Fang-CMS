# Fang CMS

Fang is a blog Content management system designed to render content as efficient, static webpages. This project is 
designed to be the backend for my personal "blog" at https://www.linuxdragon.dev/ where I intend to write everything 
from short stories, to poems, to professional articles about computing technology and software engineering. My reasons 
for writing this software is primarily because I wanted to make a project using Flask and, more specifically, Python. 
It is named after Avatar Roku's Spirit Animal, a dragon named Fang, from Avatar: The Last Airbender.

## Licensing and Permissions:
All software, images, and designs are protected copyrighted work in the US and other countries. 
Copyright :copyright: 2019 E. L. Jackson. No other entity, university, employer, organization, or individual 
has a reasonable claim to copyright on this protected work.
```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```

If you would like to use this on your own server or within your own project - whether in part or in whole, you may do so. 
However, you must follow all rules set forth by the GNU Affero General Public License, version 3 or later; and you may
not use any images or graphics that I upload to this repository, whether by accident or not, in your own copies or 
distributions.

## Instructions for Deployment:
At the moment, deployment must be performed manually. In the future, I hope to set up a docker image for this application. 
Regardless of the method used to deploy the software, certain environment configurations must be done within a TOML file. 
The file must be named `config.toml` and placed within the `/instance/`directory. An example TOML file is included in 
[this repository's instance directory](https://github.com/LinuxDragon57/Fang-CMS/blob/master/instance/config.toml.example).

### Rules for Configuration of the TOML File:
- The first step is to choose the database for use with the application's SQLALCHEMY library. This is set using the
SQLALCHEMY_DATABASE_URI application environment variables. This can be accomplished with the following formula: 
`dialect+driver://username:password@host:port/database`. Examples can be found on the official 
[Flask-SQLAlchemy documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format).
- The APP_URL application environment variable primarily functions as a whitelist for specified domains.
Clients trying to access the software with a domain that is not included in this list will be barred from accessing it.
- The DATA_DIRECTORY application environment variable is super important. In particular, it must be a full path starting
from the root of the operating system. Furthermore, it must end on a directory and not leave a trailing slash.
- The GENRES application environment variable is also super important. Only post metadata is stored in the database. The
markdown compatible content is stored in the filesystem. The application uses these genres to create directories of the
same name within the DATA_DIRECTORY. Subsequently, markdown files are stored in the directory corresponding to their 
genre categorization.

### Initial Setup of the Application:
1) Set configuration variables in `config.toml`
2) Initialize the database by running `$flask init-db`
3) Create the data directories by running `$flask mkdatadirs`
4) Create an author that can log in by running `$flask create-author --admin`. Omit the admin flag to create an 
unprivileged account.

### Rules for Manual Deployment using Gunicorn + Nginx
More information will be given after I deploy it to my server for the first time.

## Code and Releases:
This project's code tries to largely follow Functional design patterns - though admittedly, I am not as familiar with
Functional Programming; nor is Python a Functional Language. The main exception is the implementation of the 
Flask-SQLAlchemy API which uses an Object-Oriented approach, and some functions do not handle state in a Functional way. 
I do hope to get this in-line with Functional design patterns as time progresses. Most variables in this program enforce
static typing as well, and it tries to follow PEP 8 guidelines. The frontend uses TypeScript instead of JavaScript, 
and frontend code is only used when necessary for dynamic UI elements. Everything else is written in the Jinja2 
Templating language and SCSS. This project also uses [Normform](https://normform.netlify.app/) for styling forms. 
The only change that has been made is converting the CSS file to a Sass Module. The same has also been done for 
[Normalize.css](https://necolas.github.io/normalize.css/).

