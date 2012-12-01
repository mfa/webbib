# -*- coding: utf-8 -*-

import os

from jinja2 import FileSystemLoader
from flask import Flask, url_for, render_template
from flaskext.babel import Babel

class Flask(Flask):
    def create_global_jinja_loader(self):
        template_path = os.path.join(self.config.get('SOURCE', ''),
                                     "_templates")
        builtin_templates = os.path.join(self.root_path,
                                         self.template_folder)
        return FileSystemLoader([template_path, builtin_templates])
        
app = Flask("webbib")

def set_source(app, source_path=os.getcwd()):
    app.config['SOURCE'] = source_path
    source_static_folder = os.path.join(source_path, "_static")
    if os.path.isdir(source_static_folder):
        app.static_folder = source_static_folder

    app.config.from_pyfile(os.path.join(app.config['SOURCE'], 'config.py'),
                           silent=False) # True
set_source(app)
babel = Babel(app)


