from extensions import db

class Company(db.Model):
    __tablename__ = 'companies'  # Adjust the table name as needed

    id = db.Column(db.Integer, primary_key=True)
    sr_no = db.Column(db.Integer)
    name = db.Column(db.String(100))
    domain = db.Column(db.String(100))
    year_founded = db.Column(db.Integer)
    industry = db.Column(db.String(100))
    size_range = db.Column(db.String(50))
    locality = db.Column(db.String(100))
    country = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(200))
    current_employee = db.Column(db.Integer)
    total_employee = db.Column(db.Integer)
