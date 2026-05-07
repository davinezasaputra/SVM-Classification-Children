import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Buat user admin default jika belum ada
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123'), nama='Admin Puskesmas'))
            db.session.commit()
            
    MODE_DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    app.run(debug=MODE_DEBUG)