# LinuxDragon_CMS
A blog content management system designed to render content as efficient, static pages using the Flask microframework.
This project currently is unnamed. For now, it is called linuxdragon_cms because it is a cms for my domain: https://www.linuxdragon.dev

## Liscensing and Permissions
All software, images, and designs are protected copyrighted work in the US and other countries. Copyright :copyright: 2019 E. L. Jackson.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

If you would like to use this on your own server, you may do so. However, you must follow all guidelines set forth by the Affero General Public License,
version 3 or later; and you may not use any images or graphics that I upload to this repository, whether by accident or not, in your own copies or distributions.
Furthermore, I request that you create your own design aesthetic and color scheme.

## Releases
Future iterations of the program will add the following features in order of importance to me:
  1. Support for the WebAuthn protocol. 
      * I personally will not use this on my own server without having this implemented.
      * I am honestly very worried about the login system having vulnerabilities. 
        If you find them, please create a PR.
  2. A More efficient way of retreiving data for displaying the blog posts. 
      * I recently noticed the existence of a `.html.md` file extension in a URI. 
        Since this program uses Markdown for creating and storing content, I'd like 
        to look more into this and see if I can create a less database intesive way of 
        retrieving information.
      * If I am able to get the browser to merely render markdown pages as HTML automatically, 
        it will fundamentally change the way it stores files, which will create breakage.
  3. Complete the structural design of the webpages. 
      * Currently, the project's structure is mostly defined within the HTML. 
        There are many parts of this HTML structure that make no sense without the CSS.
      * These parts are important to the website's structure rather than it's aesthetic.
