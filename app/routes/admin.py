from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)


@admin_bp.route('/users')
@login_required
def users():
    admin_required()
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
def change_role(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin.users'))

    new_role = request.form.get('role')
    if new_role in ('admin', 'instructor', 'student'):
        user.role = new_role
        db.session.commit()
        flash(f'Role of {user.username} updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'info')
    return redirect(url_for('admin.users'))
