from flask import Blueprint, request, render_template
from flask_login import login_required
from ..models.company_data import Company
from ..extensions import db

query_bp = Blueprint('query', __name__)

@query_bp.route('/query_builder', methods=['GET'])
@login_required
def query_builder():
    return render_template('query_builder.html')

@query_bp.route('/query_results', methods=['GET', 'POST'])
@login_required
def query_results():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    filters = {key: value for key, value in request.form.items() if value.strip()}

    query = db.session.query(Company).filter_by(**filters)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items

    final_response = [{
        "name": row.name or None,
        "domain": row.domain or None,
        "year_founded": row.year_founded or None,
        "industry": row.industry or None,
        "size_range": row.size_range or None,
        "locality": row.locality or None,
        "country": row.country or None,
        "linkedin_url": row.linkedin_url or None,
        "current_employee": row.current_employee or None,
        "total_employee": row.total_employee or None,
    } for row in results]

    if not final_response:
        return render_template('query_builder.html', message='No data found', filters=filters)

    return render_template('query_result.html', data=final_response, filters=filters, pagination=pagination)
