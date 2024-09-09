import pandas as pd
from ..extensions import db
from ..models.company_data import Company

def process_file(file_path):
    try:
        data_in_chunks = pd.read_csv(file_path, chunksize=100000)
        record = []
        for data in data_in_chunks:
            if data.columns[0] != 'sr_no':
                data.rename(columns={data.columns[0]: 'sr_no'}, inplace=True)

            for index, row in data.iterrows():
                new_record = Company(
                    sr_no=int(row['sr_no']),
                    name=row['name'],
                    domain=row['domain'],
                    year_founded=int(row['year founded']) if pd.notna(row['year founded']) else None,
                    industry=row['industry'],
                    size_range=row['size range'],
                    locality=row['locality'],
                    country=row['country'],
                    linkedin_url=row['linkedin url'],
                    current_employee=int(row['current employee estimate']) if pd.notna(row['current employee estimate']) else None,
                    total_employee=int(row['total employee estimate']) if pd.notna(row['total employee estimate']) else None
                )
                record.append(new_record)

            db.session.bulk_save_objects(record)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while processing the file: {e}")
