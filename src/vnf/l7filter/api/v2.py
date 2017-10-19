from flask import Blueprint, request, jsonify
import xmltodict
from controllers.AbstractFlowController import AbstractFlowController
from helpers.CommonHelper import getValIfKeyExists

v2 = Blueprint('v2', __name__, template_folder='templates')


@v2.route('/getFlow/v2', methods=['POST'])
def get_flow_v2():
    json_content = request.json
    print(json_content)
    abstract_flow_controller = AbstractFlowController()
    response = abstract_flow_controller.getOvsFlow(json_content)
    return jsonify(response)

@v2.route('/createFlowsXML/v2', methods=['POST'])
def createXML_v2():
    xml_datas = []
    rules = xmltodict.parse(request.data, dict_constructor=dict)["mspl-set"]["it-resource"]["configuration"]["rule"]
    if isinstance(rules, list):
        for rule in rules:
            xml_datas.append(rule)
    else:
        xml_datas.append(rules)

    print(xml_datas)
    rate_limit = None
    dict_flows = []
    for xml_data in xml_datas:
        if getValIfKeyExists(xml_data["condition"],"traffic-flow-condition") is not None:
            rate_limit = getValIfKeyExists(xml_data["condition"]["traffic-flow-condition"], "rate-limit")
        dict_flows.append({
            "ip_src": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "source-address"),
            "ip_dst": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "destination-address"),
            "priority": getValIfKeyExists(xml_data, "priority"),
            "protocol": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "protocol"),
            "port_src": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "source-port"),
            "port_dst": getValIfKeyExists(xml_data["condition"]["packet-filter-condition"], "destination-port"),
            "actions": getValIfKeyExists(xml_data, "action"),
            "rate_limit": rate_limit
        })


    # response = "Test.."
    # response = AbstractFlowController(json_events=dict_flows).set_flows()
    response = AbstractFlowController(json_events=dict_flows).set_flows_performance()


    # FlowController(globalVar.current_flow_list, json_events=json_data).set_flows()
    # print("########### RULES END #############")
    # print(globalVar.current_flow_list)
    return jsonify(response)

@v2.route('/deleteFlow/v2', methods=['DELETE'])
def delete():
    flow_controller = AbstractFlowController()
    content_dict = {
                    "id": int(request.args.get('id'))
                   }
    print(content_dict)
    # flow_controller.deleteFlow(content_dict)
    flow_controller.deleteOvsFlow(content_dict)
    # return jsonify(response)
    return "Flow deleted!"

@v2.route('/deleteAllFlows/v2', methods=['DELETE'])
def deleteAllFlows():
    flow_controller = AbstractFlowController()
    # flow_controller.deleteAllFlows()
    flow_controller.deleteAllOvsFlows()
    # return jsonify(response)
    return "Flow deleted!"