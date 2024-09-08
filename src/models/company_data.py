from extensions import db

class Company(db.Model):
    __tablename__ = 'companies'  # Adjust the table name as needed

    id = db.Column(db.Integer, primary_key=True)
    sr_no = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=True)
    domain = db.Column(db.String(100), nullable=True)
    year_founded = db.Column(db.Integer, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    size_range = db.Column(db.String(50), nullable=True)
    locality = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    current_employee = db.Column(db.Integer, nullable=True)
    total_employee = db.Column(db.Integer, nullable=True)
