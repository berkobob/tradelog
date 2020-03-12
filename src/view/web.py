from flask import Blueprint, render_template, request, flash, redirect
from src.controller.tradelog import create_portfolio, ports

web = Blueprint('web', __name__)

@web.route('/')
def home():
    """ Render the home page """
    return render_template('home.html', ports=ports())

@web.route('/new', methods=['GET', 'POST'])
def new():
    """ Create a new portfolio """
    if request.method == 'POST':
        port = {'name': request.form['name'],
                'description': request.form['description']}
        result = create_portfolio(port)
        if result.success:
            flash (f'{port["name"]} successfully created', 'SUCCESS')
        else:
            flash (result.message, result.severity)

    return render_template('new.html', ports=ports())


@web.route('/load', methods=['GET', 'POST'])
def load():
    if request.method == 'GET': return render_template('load.html', ports=ports())

    f = request.files['file']
    try:
        f.save(f.filename)
    except Exception as e:
        flash(str(e), 'ERROR')
        return render_template('load.html', ports=ports())
    return render_template('load.html', ports=ports())


#     trades = []
#     try:
#         with open(f.filename) as file:
#             headers = file.readline().split(',')
#             for row in file:
#                 trade = dict(zip(headers, row.split(',')))
#                 trades.append(trade)
#                 # trade = Trade(trade)
#                 print(trade)
#     except Exception as e:
#         flash(str(e),'ERROR')
    
#     flash(f'{f.filename} loaded successfully!', 'SUCCESS')
#     return render_template('rawtrades.html', trades=trades)