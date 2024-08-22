from flask import Blueprint, jsonify, request, url_for, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Prediction, Image
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os
from io import BytesIO

bp = Blueprint('history', __name__)

@bp.route('/view_prediction_history', methods=['GET'])
@jwt_required()
def view_prediction_history():
    user_id = get_jwt_identity()['id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

    query = db.session.query(
        Prediction.id,
        Prediction.image_id,
        Prediction.predicted_class,
        Prediction.confidence_percentage,
        Prediction.prediction_date,
        Image.image_path
    ).join(Image, Prediction.image_id == Image.id).filter(Prediction.user_id == user_id)

    if start_date:
        query = query.filter(Prediction.prediction_date >= start_date)
    if end_date:
        query = query.filter(Prediction.prediction_date <= end_date)

    predictions = query.order_by(Prediction.prediction_date.desc()).all()

    predictions_list = [{
        'id': p.id,
        'image_id': p.image_id,
        'predicted_class': p.predicted_class,
        'confidence_percentage': p.confidence_percentage,
        'prediction_date': p.prediction_date,
        'image_url': url_for('uploaded_file', filename=os.path.basename(p.image_path), _external=True),
        'image_path': p.image_path
    } for p in predictions]

    return jsonify(predictions_list), 200

@bp.route('/download_prediction_history_pdf', methods=['GET'])
@jwt_required()
def download_prediction_history_pdf():
    user_id = get_jwt_identity()['id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

    query = db.session.query(
        Prediction.id,
        Prediction.image_id,
        Prediction.predicted_class,
        Prediction.confidence_percentage,
        Prediction.prediction_date,
        Image.image_path
    ).join(Image, Prediction.image_id == Image.id).filter(Prediction.user_id == user_id)

    if start_date:
        query = query.filter(Prediction.prediction_date >= start_date)
    if end_date:
        query = query.filter(Prediction.prediction_date <= end_date)

    predictions = query.order_by(Prediction.prediction_date.desc()).all()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add header image
    header_path = os.path.join(os.path.dirname(__file__), '../static/images/header_image1.jpg')
    if os.path.exists(header_path):
        header_width, header_height = 600, 80
        p.drawImage(header_path, width / 2.0 - header_width / 2.0, height - 80, width=header_width, height=header_height)


    p.setFont("Helvetica", 12)
    y_position = height - 130
    for prediction in predictions:
        image_path = prediction.image_path
        if os.path.exists(image_path):
            p.drawImage(image_path, 50, y_position - 50, width=75, height=75)
        else:
            p.drawString(50, y_position, "Image not available")

        p.drawString(160, y_position, f"Predicted Class: {prediction.predicted_class}")
        p.drawString(160, y_position - 20, f"Confidence: {prediction.confidence_percentage}%")
        p.drawString(160, y_position - 40, f"Date: {prediction.prediction_date.strftime('%Y-%m-%d %H:%M:%S')}")
        y_position -= 100

        if y_position < 100:
            p.showPage()
            y_position = height - 130

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="prediction_history.pdf", mimetype='application/pdf')
