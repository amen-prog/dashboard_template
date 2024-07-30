from flask import Blueprint, request, jsonify
from app.services.main import *

main = Blueprint('main', __name__)

@main.route('/test-post', methods=['POST'])
def test_post():
    data = request.json
    return jsonify({"message": f"Received POST request with message: {data.get('message')}"})

@main.route('/test-get', methods=['GET'])
def test_get():
    return jsonify({"message": "This is a test GET response"})


@main.route('/initialize', methods=['POST'])
def initialize():
    data = request.json
    # result = initialize_algorithm(data.get('file_path'), data.get('chg_path'))
    # return jsonify(result)

@main.route('/crop', methods=['POST'])
def crop():
    data = request.json
    # result = process_crop(data.get('crop_decision'), data.get('coordinates'))
    # return jsonify(result)

# @main.route('/process', methods=['POST'])
# def process():
#     result = final_processing()
#     return jsonify(result)