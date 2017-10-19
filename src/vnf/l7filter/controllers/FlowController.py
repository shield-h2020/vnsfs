from models import Flow
import pexpect
from helpers.DbHelper import db_session

class FlowController:

    def __init__(self, cur_flow_list=[], json_events=[]):
        # print(rule.list)
        self.flows = []
        for json_event in json_events:
            flow = Flow.Flow()
            flow.set(json_event)
            self.flows.append(flow)
            # if (json_event["source_ip"], json_event["destination_ip"]) not in cur_flow_list:
            #     if flow not in self.flows:
            #         self.flows.append(flow)
            #         cur_flow_list.append((json_event["source_ip"], json_event["destination_ip"]))


    def set_flows(self):
        print(self.flows)
        with db_session() as db:
            for flow in self.flows:
                flow.apply()
                new_id = flow.create_db(db)
                print(new_id)
            db.commit()
        return "True"

    def getFlow(self, json_content):
        flow = Flow.Flow()
        if json_content is not None and bool(json_content) is True:
            flow.set(json_content)
        response = flow.get_by_filter()
        return response

    def deleteFlow(self, json_content):
        flow = Flow.Flow()
        flow.id = json_content["id"]
        with db_session() as db:
            # flow.delete()
            # Delete from DB
            flow.delete_db(db)
            db.commit()
        return {"response": "delete_done"}