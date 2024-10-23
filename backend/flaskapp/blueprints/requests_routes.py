from flask import Blueprint, jsonify
from ..extensions import supabase  # Assuming you have initialized supabase
from ..models.requests import RequestService, RequestController
from ..models.notification import notification_engine, notification_sender


requests_blueprint = Blueprint("requests", __name__)

# Initialize services and controllers
request_service = RequestService(supabase)
request_controller = RequestController(request_service)
notif_engine = notification_engine(supabase)
notif_sender = notification_sender(notif_engine)

# Define routes
@requests_blueprint.route("/withdraw_request/<int:request_id>", methods=['DELETE'])
def withdraw_request(request_id: int):
    response, data = request_controller.withdraw_request(request_id)
    if "error" not in response.keys():
        email = notif_sender.send_withdraw(data)
        response["email"] = email
    return jsonify(response)

@requests_blueprint.route("/cancel_request/<int:request_id>", methods=['DELETE'])
def cancel_request(request_id: int):
    response, data = request_controller.cancel_request(request_id)
    if "error" not in response.keys():
        email = notif_sender.send_cancel(data)
        response["email"] = email
    return jsonify(response)

@requests_blueprint.route("/getstaffid", methods=['GET'])
def get_staff_id():
    return request_controller.get_staff_id()

@requests_blueprint.route("/requests/", methods=['POST'])
def create_request():
    response = request_controller.create_request()
    if "error" not in response.keys():
        code = notif_sender.send_create()
        response["email"] = code
    return jsonify(response)

@requests_blueprint.route("/requests/<int:staff_id>", methods=['GET'])
def get_requests_by_staff(staff_id: int):
    return request_controller.get_requests_by_staff(staff_id)

@requests_blueprint.route('/team/requests', methods=['GET'])
def get_team_requests():
    return request_controller.get_team_requests()

@requests_blueprint.route("/request/<request_id>", methods=['GET'])
def get_selected_request(request_id):
    return request_controller.get_selected_request(request_id)

@requests_blueprint.route("/request/<request_id>/approve", methods=['PUT', 'POST'])
def request_approve(request_id):
    response = request_controller.approve_request(request_id)
    if "error" not in response.keys():
        email = notif_sender.send_approve(request_id)
        response["email"] = email
    return jsonify(response)

@requests_blueprint.route("/request/<request_id>/reject", methods=['PUT'])
def request_reject(request_id):
    response = request_controller.reject_request(request_id)
    if "error" not in response.keys():
        email = notif_sender.send_reject(request_id)
        response["email"] = email
    return jsonify(response)