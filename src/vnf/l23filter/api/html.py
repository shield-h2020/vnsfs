from flask import Blueprint, render_template

html = Blueprint('html', __name__, template_folder='templates')

# ################ HTTP routes #########################
@html.route('/')
def index_html(): return render_template('index.html')

@html.route('/header')
def header_html(): return render_template('header.html')


@html.route('/sidebar')
def sidebar_html(): return render_template('sidebar.html')

@html.route('/listofrules')
def listofrules_html(): return render_template('listofrules.html')
