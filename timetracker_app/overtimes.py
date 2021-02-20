from flask import jsonify
from timetracker_app import app


@app.route('/api/v1/overtimes', methods=['GET'])
def get_overtimes():
    return jsonify({
        'success': True,
        'data': 'All overtimes'
    })


@app.route('/api/v1/overtimes/<int:overtime_id>', methods=['GET'])
def get_overtime(overtime_id: int):
    return jsonify({
        'success': True,
        'data': f'Get overtime with id {overtime_id}'
    })


@app.route('/api/v1/overtimes', methods=['POST'])
def create_overtime():
    return jsonify({
        'success': True,
        'data': 'New overtime has been created'
    }), 201


@app.route('/api/v1/overtimes/<int:overtime_id>', methods=['PUT'])
def update_overtime(overtime_id:int):
    return jsonify({
        'success': True,
        'data': f'Overtime with id {overtime_id} has been updated'
    })


@app.route('/api/v1/overtimes/<int:overtime_id>', methods=['DELETE'])
def delete_overtime(overtime_id: int):
    return jsonify({
        'success': True,
        'data': f'Overtime with id {overtime_id} has been deleted'
    })