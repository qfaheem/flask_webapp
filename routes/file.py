from flask import Blueprint, request, render_template, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from ..celery_config import celery
from ..utils.helpers import process_file

file_bp = Blueprint('file', __name__)

@file_bp.route('/upload_data', methods=['GET', 'POST'])
@login_required
def upload_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            uploads_dir = 'uploads_dir'
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)
            task = process_file.delay(file_path)
    return render_template('uploading.html')
