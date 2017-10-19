from flask import Blueprint, request, jsonify
from controllers.FlowController import FlowController
from models.Flow import Flow, get_current_flows
from helpers.CommonHelper import getValIfKeyExists
from models.GlobalModel import Global
import json
import xmltodict

v1 = Blueprint('v1', __name__, template_folder='templates')
globalVar = Global(fw_status=True)


@v1.route("/getListOfRules/v1", methods=['GET'])
def get_list_of_rules():
    return json.dumps(get_current_flows(), sort_keys=True, indent=4)

@v1.route('/getFlow/v1', methods=['POST'])
def get_flow():
    json_content = request.json
    print(json_content)
    flow_controller = FlowController()
    response = flow_controller.getFlow(json_content)
    return jsonify(response)

@v1.route('/createFlows/v1', methods=['POST'])
def create():
    # print("########### RULES START #############")
    # print(globalVar.current_flow_list)
    json_data = request.get_json()
    # print("########### DATA #############")
    # print(json_data)
    FlowController(globalVar.current_flow_list, json_events=json_data).set_flows()
    # print("########### RULES END #############")
    # print(globalVar.current_flow_list)
    return "Flow created!"

@v1.route('/deleteFlow/v1', methods=['DELETE'])
def delete():
    flow_controller = FlowController()
    json_content = {
                    "id": int(request.args.get('id'))
                   }
    print(json_content)
    flow_controller.deleteFlow(json_content)
    # return jsonify(response)
    return "Flow deleted!"

@v1.route('/deleteAllFlows/v1', methods=['DELETE'])
def delete_all():
    # print("########### RULES START #############")
    # print(globalVar.current_flow_list)
    for flow in globalVar.current_flow_list:
        # print(flow)
        Flow(flow[0], flow[1]).delete()
        # globalVar.current_flow_list.remove(flow)
    globalVar.current_flow_list = []
    # print("########### RULES END #############")
    # print(globalVar.current_flow_list)
    return "Flows deleted!"


@v1.route('/createFlowsXML/v1', methods=['POST'])
def createXML_v1():
    xml_data = xmltodict.parse(request.data, dict_constructor=dict)["mspl-set"]["it-resource"]["configuration"]["rule"]
    # print(xml_data)

    tcp_src_port = None
    tcp_dst_port = None
    udp_src_port = None
    udp_dst_port = None

    protocol = getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "protocol")

    if protocol == "TCP":
        tcp_src_port = getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "source-port")
        tcp_dst_port = getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "destination-port")
    elif protocol == "UDP":
        udp_src_port = getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "source-port")
        udp_dst_port = getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "destination-port")


    dict_flow = {
        "nw_src": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "source-address"),
        "nw_dst": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "destination-address"),
        "priority": getValIfKeyExists(xml_data, "priority"),
        "protocol": protocol,
        "tcp_src": tcp_src_port,
        "tcp_dst": tcp_dst_port,
        "udp_src": udp_src_port,
        "udp_dst": udp_dst_port,
        "actions": getValIfKeyExists(xml_data, "action")
    }

    FlowController(json_events=[dict_flow]).set_flows()
    # FlowController(globalVar.current_flow_list, json_events=json_data).set_flows()
    # print("########### RULES END #############")
    # print(globalVar.current_flow_list)
    return "Flow created!"
