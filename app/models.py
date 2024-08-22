from app import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_path = db.Column(db.String(255))
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('images', lazy=True))

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    predicted_class = db.Column(db.String(100))
    confidence_percentage = db.Column(db.Float)
    prediction_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('predictions', lazy=True))
    image = db.relationship('Image', backref=db.backref('prediction', uselist=False))

class PlantDisease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_name = db.Column(db.String(50))
    disease_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    causes = db.Column(db.Text)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class CureSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('plant_disease.id'))
    suggestion = db.Column(db.Text)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    plant_disease = db.relationship('PlantDisease', backref=db.backref('cure_suggestions', lazy=True))

class UserSatisfactionSurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    satisfaction = db.Column(db.String(50))
    usefulness = db.Column(db.Text)  # Store as a comma-separated string
    desired_features = db.Column(db.Text)  # Store as a comma-separated string
    recommendation = db.Column(db.String(50))
    survey_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('surveys', lazy=True))

def insert_initial_data():
    if PlantDisease.query.first() is not None:
        # Data already exists, no need to insert
        return

    diseases = [
        ('Corn', 'Corn___Common_rust', 'Common rust is a fungal disease of corn.', 'Small, reddish-brown pustules on leaves.', 'Caused by the fungus Puccinia sorghi.'),
        ('Corn', 'Corn___Gray_leaf_spot', 'Gray leaf spot is a fungal disease of corn.', 'Lesions are initially small and rectangular, turning grayish as the disease progresses.', 'Caused by the fungus Cercospora zeae-maydis.'),
        ('Corn', 'Corn___Northern_Leaf_Blight', 'Northern leaf blight is a fungal disease affecting corn leaves.', 'Elliptical, gray-green lesions on leaves.', 'Caused by the fungus Exserohilum turcicum.'),
        ('Corn', 'Corn___healthy', 'This is a healthy corn plant with no diseases.', 'No symptoms.', 'No causes.'),
        ('Potato', 'Potato___Early_blight', 'Early blight is a fungal disease affecting potato leaves and stems.', 'Small, dark, concentric lesions on leaves.', 'Caused by the fungus Alternaria solani.'),
        ('Potato', 'Potato___Late_blight', 'Late blight is a serious fungal disease affecting potatoes.', 'Dark, water-soaked lesions on leaves and stems, white fungal growth under humid conditions.', 'Caused by the oomycete Phytophthora infestans.'),
        ('Potato', 'Potato___healthy', 'This is a healthy potato plant with no diseases.', 'No symptoms.', 'No causes.'),
        ('Strawberry', 'Strawberry___Leaf_scorch', 'Leaf scorch is a fungal disease affecting strawberry leaves.', 'Irregular, brown, and dead areas on leaves, often with a yellow halo.', 'Caused by the fungus Diplocarpon earliana.'),
        ('Strawberry', 'Strawberry___healthy', 'This is a healthy strawberry plant with no diseases.', 'No symptoms.', 'No causes.'),
        ('Unknown', 'Unknown___Unexpected_input', 'This is an unknown or unexpected input.', 'No symptoms.', 'No causes.')
    ]

    suggestions = [
        ('Corn___Common_rust', 'Apply a fungicide such as azoxystrobin or pyraclostrobin to control the spread of common rust. Ensure good air circulation by proper spacing of plants. Remove and destroy affected plant debris to reduce sources of infection.'),
        ('Corn___Gray_leaf_spot', 'Use resistant hybrids and practice crop rotation to reduce disease pressure. Apply fungicides like strobilurins or triazoles at the first sign of disease. Maintain good field sanitation by removing and destroying crop debris.'),
        ('Corn___Northern_Leaf_Blight', 'Apply fungicides such as mancozeb or chlorothalonil when disease is first observed. Rotate crops to avoid planting corn in the same field year after year. Use resistant corn varieties to reduce the likelihood of infection.'),
        ('Corn___healthy', 'No action is needed for healthy plants. Continue to monitor regularly for any signs of disease and maintain good agricultural practices to keep plants healthy.'),
        ('Potato___Early_blight', 'Apply fungicides like maneb or copper-based fungicides at regular intervals. Ensure proper spacing of plants to improve air circulation and reduce humidity around plants. Remove and destroy infected plant debris.'),
        ('Potato___Late_blight', 'Use fungicides such as metalaxyl or dimethomorph to protect plants from late blight. Destroy infected plants immediately to prevent the spread of the disease. Ensure good drainage in the field to reduce the likelihood of infection.'),
        ('Potato___healthy', 'No action is needed for healthy plants. Continue to monitor regularly for any signs of disease and maintain good agricultural practices to keep plants healthy.'),
        ('Strawberry___Leaf_scorch', 'Remove and destroy infected leaves to reduce the spread of leaf scorch. Apply appropriate fungicides such as captan or myclobutanil. Ensure proper irrigation practices to avoid wetting the foliage.'),
        ('Strawberry___healthy', 'No action is needed for healthy plants. Continue to monitor regularly for any signs of disease and maintain good agricultural practices to keep plants healthy.'),
        ('Unknown___Unexpected_input', 'N/A')
    ]

    # Insert PlantDiseases
    for plant_name, disease_name, description, symptoms, causes in diseases:
        disease = PlantDisease(
            plant_name=plant_name,
            disease_name=disease_name,
            description=description,
            symptoms=symptoms,
            causes=causes
        )
        db.session.add(disease)
    
    db.session.commit()

    # Insert CureSuggestions
    for disease_name, suggestion in suggestions:
        disease = PlantDisease.query.filter_by(disease_name=disease_name).first()
        if disease:
            cure_suggestion = CureSuggestion(
                disease_id=disease.id,
                suggestion=suggestion
            )
            db.session.add(cure_suggestion)
    
    db.session.commit()
