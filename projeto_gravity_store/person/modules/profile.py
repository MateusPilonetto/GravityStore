from flask import Blueprint, render_template

profile_bp = Blueprint('profile', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/static/profile')

@profile_bp.route('/profile')
def profile():
    return render_template('person.html')