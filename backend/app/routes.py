from flask import Blueprint, request, jsonify
from app.services.main import step1
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

def ensure_upload_directory():
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@main.route('/test-post', methods=['POST'])
def test_post():
    data = request.json
    return jsonify({"message": f"Received POST request with message: {data.get('message')}"})

@main.route('/test-get', methods=['GET'])
def test_get():
    return jsonify({"message": "This is a test GET response"})


@main.route('/initialize', methods=['POST'])
def initialize():
    operator_name = request.form.get('operatorName')
    project_name = request.form.get('siteName')
    folder_option = request.form.get('folderOption')

    target_folder = None
    if folder_option == '3':
        # Change to Another Folder
        target_folder = request.form.get('customFolderPath')
    
    upload_dir = ensure_upload_directory()
    image_path = None

    # Handle file upload
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        if file.filename != '':
            filename = secure_filename(file.filename)
            image_path = os.path.join(upload_dir, filename)
            print(f"Attempting to save file to: {image_path}")
            file.save(image_path)
            print(f"File saved successfully to: {image_path}")
    
    # result = step1(operator_name, project_name, folder_option, target_folder, image_path, has_offsite_emissions)

    # return jsonify(result)

    return jsonify({
        "message": "Data received successfully",
        "operatorName": operator_name,
        "projectName": project_name,
        "imgPath": image_path
    })

@main.route('/boundaries', methods=['POST'])
def boundaries():
    # Check if the request is JSON (from Step2) or form data (from Step1)
    if request.is_json:
        has_offsite_emissions = request.json.get('hasOffsiteEmissions')
        return jsonify({
            "message": "Received offsite emissions data",
            "hasOffsiteEmissions": has_offsite_emissions
        })

@main.route('/polygon', methods=['POST'])
def polygon():
    # Check if the request is JSON (from Step2) or form data (from Step1)
    data = request.json
    polygon = data.get('polygon')
    coords = polygon['geometry']['coordinates'][0]
    
    # Here you can process and store the polygon data as needed
    # For example, you might want to save it to a database
    
    print("Received polygon:", polygon)
    
    return jsonify({"message": "Polygon received successfully",
                    "polygon": coords})

@main.route('/equipment', methods=['POST'])
def equipment():
    data = request.json
    equipment_data = data.get('equipmentData', [])
    
    processed_equipment = []
    
    for item in equipment_data:
        equipment = item.get('equipment', {})
        polygon = item.get('polygon', {})
        
        equipment_info = {
            'id': equipment.get('id'),
            'name': equipment.get('name'),
            'sourceHeight': equipment.get('sourceHeight'),
            'isEmissionSource': equipment.get('isEmissionSource')
        }
        
        coords = polygon.get('geometry', {}).get('coordinates', [[]])[0]
        
        processed_item = {
            'equipment': equipment_info,
            'coordinates': coords
        }
        
        processed_equipment.append(processed_item)
        
        # Here you can process and store the equipment and polygon data as needed
        # For example, you might want to save it to a database
        
        print(f"Received equipment: {equipment_info['name']}")
        print(f"With polygon: {coords}")
    
    return jsonify({
        "message": f"Received {len(processed_equipment)} equipment items successfully",
        "equipment": processed_equipment
    })