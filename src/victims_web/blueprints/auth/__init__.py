# This file is part of victims-web.
#
# Copyright (C) 2013 The Victims Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Authentication related views.
"""

from flask import (
    Blueprint, current_app, escape, flash, render_template, request,
    url_for, redirect)

from flask.ext.login import fresh_login_required, login_required, current_user
from mongoengine import ValidationError

from victims_web.handlers.forms import (
    AccountEditForm, RegistrationForm, flash_errors)
from victims_web.handlers.security import login, logout, safe_redirect_url
from victims_web.user import create_user, get_account

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route("/login", methods=['GET', 'POST'])
def login_user():
    def redirect_url():
        forward = safe_redirect_url()
        if not forward:
            flash("Logged in successfully.", category='info')
        return redirect(forward or url_for('ui.index'))

    # If you are already logged in, go away!
    if not current_user.is_anonymous():
        return redirect_url()

    if request.method == 'POST':
        username = request.form.get('username', '')
        if login(username, request.form.get('password', '')):
            return redirect_url()

        flash("Invalid username/password", category='error')

    return render_template("login.html")


@auth.route("/logout", methods=['GET'])
@login_required
def logout_user():
    logout()
    return redirect(url_for('ui.index'))


@auth.route('/account', methods=['GET'])
@login_required
def user_account():
    account = get_account(current_user.username)
    content = {
        'username': account.username,
        'email': account.email,
        'apikey': str(account.apikey),
        'secret': str(account.secret),
    }
    return render_template('account.html', **content)


@auth.route('/account/edit', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def user_edit():
    form = AccountEditForm()

    if form.validate_on_submit():
        try:
            account = get_account(current_user.username)
            if form.change_password.data:
                if form.password.data == current_user.username:
                    raise ValidationError(
                        'Password can not be the same as the username.')
                account.set_password(form.password.data)

            if form.change_email.data:
                email = form.email.strip()
                account.email = email if len(email) > 0 else None

            if form.regenerate.data:
                account.update_api_tokens()

            account.validate()
            account.save()
            flash('Account information was successfully updated!',
                  category='info')
            return redirect(url_for('auth.user_account'))
        except ValueError as ve:
            flash(ve.message, category='error')
        except ValidationError as ve:
            invalids = ','.join([f.title() for f in ve.errors.keys()])
            msg = 'Invalid: %s' % (invalids)
            flash(escape(msg), category='error')
        except Exception as ex:
            current_app.logger.info(ex)
            flash('An unknown error has occured.', category='error')

    return render_template('account_edit.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register_user():
    if current_user.is_authenticated():
        flash(
            'You are already logged in as %s' % (escape(current_user.username))
        )
        return redirect(url_for('ui.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            email = form.email.data.strip()

            if len(email) == 0:
                email = None

            create_user(username, password, email)
            login(username, password)

            flash('Registration successful, welcome %s!' % (username),
                  category='info')
            return redirect(url_for('ui.index'))
        except ValidationError, ve:
            invalids = ','.join([f.title() for f in ve.errors.keys()])
            msg = 'Invalid: %s' % (invalids)
            flash(escape(msg), category='error')
        except ValueError, ve:
            flash(escape(ve.message), category='error')
        except Exception, ex:
            current_app.logger.info(ex)
            flash('An unknown error has occured.', category='error')
    else:
        flash_errors(form)

    return render_template('register.html', form=form)
