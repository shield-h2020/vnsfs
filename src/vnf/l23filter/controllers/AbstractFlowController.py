from models import AbstractFlow
import pexpect
from helpers.DbHelper import db_session
from helpers.CommonHelper import getValIfKeyExists
from models import AbstractFlow, OvsFlow
from configuration import config as cnf
from helpers.DbHelper import on_connect, db_session

class AbstractFlowController:

    def __init__(self, json_events=[]):
        # print(rule.list)
        self.abstract_flows = []
        for json_event in json_events:
            abstract_flow = AbstractFlow.AbstractFlow()
            abstract_flow.set(json_event)
            self.abstract_flows.append(abstract_flow)

    def set_flows(self):
        print(self.abstract_flows)
        new_ids = []
        with db_session() as db:
            for abstract_flow in self.abstract_flows:
                new_id = abstract_flow.create_db(db)
                if abstract_flow.actions == "drop":
                    abstract_flow.ovs_flow.apply()
                elif abstract_flow.actions == "accept":
                    abstract_flow.traffic_control_flow.apply()
                print(new_id)
                new_ids.append({ "id": new_id })
            db.commit()
        return new_ids
        # TODO: need to return a higher level object id
        # return { "id": new_id }

    def set_flows_performance(self):
        with db_session() as db:

            for abstract_flow in self.abstract_flows:
                abstract_flow.ovs_flow.apply()

            db.execute(
                OvsFlow.OvsFlow.__table__.insert(),
                [{  "nw_src": abstract_flow.ovs_flow.nw_src,
                    "nw_dst": abstract_flow.ovs_flow.nw_dst,
                    "n_packets": abstract_flow.ovs_flow.n_packets,
                    "n_bytes": abstract_flow.ovs_flow.n_bytes,
                    "cookie": abstract_flow.ovs_flow.cookie,
                    "idle_age": abstract_flow.ovs_flow.idle_age,
                    "duration": abstract_flow.ovs_flow.duration,
                    "priority": abstract_flow.ovs_flow.priority,
                    "table": abstract_flow.ovs_flow.table,
                    "protocol": abstract_flow.ovs_flow.protocol,
                    "tcp_src": abstract_flow.ovs_flow.tcp_src,
                    "tcp_dst": abstract_flow.ovs_flow.tcp_dst,
                    "udp_src": abstract_flow.ovs_flow.udp_src,
                    "udp_dst": abstract_flow.ovs_flow.udp_dst,
                    "actions": abstract_flow.ovs_flow.actions
                 } for abstract_flow in self.abstract_flows]
            )


            db.commit()
        return "Flows added!"




    def getFlow(self, dict_content):
        abstract_flow = AbstractFlow.AbstractFlow()
        if dict_content is not None and bool(dict_content) is True:
            abstract_flow.set(dict_content)
        response = abstract_flow.get_by_filter()
        return response

    def getOvsFlow(self, dict_content):
        ovs_flow = OvsFlow.OvsFlow()
        if dict_content is not None and bool(dict_content) is True:
            ovs_flow.set(dict_content)
        response = ovs_flow.get_by_filter(transform_to_abstract_flow=True)
        return response

    def deleteFlow(self, json_content):
        with db_session() as db:
            # Delete from DB
            abstract_flow = db.query(AbstractFlow.AbstractFlow).get(json_content["id"])
            if abstract_flow.actions == "drop":
                abstract_flow.ovs_flow.delete()
            elif abstract_flow.actions == "accept":
                abstract_flow.traffic_control_flow.delete()
            abstract_flow.delete_db(db)
            db.commit()
        return {"response": "delete_done"}


    def deleteOvsFlow(self, json_content):
        with db_session() as db:
            # Delete from DB
            ovs_flow = db.query(OvsFlow.OvsFlow).get(json_content["id"])
            ovs_flow.delete()
            ovs_flow.delete_db(db)
            db.commit()
        return {"response": "delete_done"}

    def deleteAllFlows(self):
        with db_session() as db:
            abstract_flow = AbstractFlow.AbstractFlow()
            flows = abstract_flow.get_by_filter_obj(db)
            for abstract_flow in flows:
                # Delete from DB
                if abstract_flow.actions == "drop":
                    abstract_flow.ovs_flow.delete()
                elif abstract_flow.actions == "accept":
                    abstract_flow.traffic_control_flow.delete()
                abstract_flow.delete_db(db)
            db.commit()
        return {"response": "delete_done"}

    def deleteAllOvsFlows(self):
        with db_session() as db:
            ovs_flow = OvsFlow.OvsFlow()
            flows = ovs_flow.get_by_filter_obj(db)
            for ovs_flow in flows:
                # Delete from DB
                ovs_flow.delete()
            num_rows_deleted = db.query(OvsFlow.OvsFlow).delete()
            db.commit()
        return {"num_rows_deleted": num_rows_deleted}