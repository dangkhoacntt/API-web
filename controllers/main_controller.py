from flask import Blueprint, render_template, redirect, url_for, session, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
def home():
    if 'user_email' in session:
        return render_template('frontend/home.html', user=session['user_email'])
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login'))

@main_bp.route('/funcaptcha')
def funcaptcha():
    if 'user_email' in session:
        return render_template('frontend/arkoselabs-funcaptcha.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login'))
