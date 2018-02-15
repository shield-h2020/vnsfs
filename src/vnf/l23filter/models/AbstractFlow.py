import helpers.CommandExecutionHelper as CommandExecutionHelper
import pexpect

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, and_
from sqlalchemy.orm import relationship, backref
from models.Base import Base
from models.OvsFlow import OvsFlow
from models.TrafficControlFlow import TrafficControlFlow
from helpers.DbHelper import on_connect, db_session
from helpers.CommonHelper import getValIfKeyExists


class AbstractFlow(Base):
    __tablename__ = 'abstract_flow'

    id = Column(Integer, primary_key=True)
    ip_src = Column(String(16), nullable=True)
    ip_dst = Column(String(16), nullable=True)


    priority = Column(Integer, nullable=True)

    protocol = Column(String(32), nullable=True)
    port_src = Column(Integer, nullable=True)
    port_dst = Column(Integer, nullable=True)
    rate_limit = Column(Integer, nullable=True)

    actions = Column(String(64), nullable=True)

    ovs_flow = relationship("OvsFlow", uselist=False, backref="ovs_flow", cascade="all,delete")
    traffic_control_flow = relationship("TrafficControlFlow", uselist=False, backref="traffic_control_flow", cascade="all,delete")

    def __repr__(self):
        return "<AbstractFlow(id='%s', ip_src='%s', ip_dst='%s', priority='%s', protocol='%s', port_src='%s', " \
               "port_dst='%s' rate_limit='%s' actions='%s')>" % \
               (self.id, self.ip_src, self.ip_dst, self.priority, self.protocol, self.port_src, self.port_dst,
                self.rate_limit, self.actions)

    def set(self, dict_representation):
        self.id = getValIfKeyExists(dict_representation, "id")
        self.ip_src = getValIfKeyExists(dict_representation, "ip_src")
        self.ip_dst = getValIfKeyExists(dict_representation, "ip_dst")
        self.priority = getValIfKeyExists(dict_representation, "priority")
        self.protocol = getValIfKeyExists(dict_representation, "protocol").lower()
        self.port_src = getValIfKeyExists(dict_representation, "port_src")
        self.port_dst = getValIfKeyExists(dict_representation, "port_dst")
        self.rate_limit = getValIfKeyExists(dict_representation, "rate_limit")
        self.actions = getValIfKeyExists(dict_representation, "actions")

        def abstract_to_ovs_flow(abstract_dict):
            tcp_src_port = None
            tcp_dst_port = None
            udp_src_port = None
            udp_dst_port = None
            if getValIfKeyExists(abstract_dict, "protocol").lower() == "tcp":
                print("*********************TCP************************")
                tcp_src_port = getValIfKeyExists(abstract_dict, "port_src")
                tcp_dst_port = getValIfKeyExists(abstract_dict, "port_dst")
            elif getValIfKeyExists(abstract_dict, "protocol").lower() == "udp":
                print("*********************UDP************************")
                udp_src_port = getValIfKeyExists(abstract_dict, "port_src")
                udp_dst_port = getValIfKeyExists(abstract_dict, "port_dst")

            print("*********************************************")
            print(getValIfKeyExists(abstract_dict, "protocol").lower())
            print(tcp_src_port)
            print(tcp_dst_port)
            print(udp_src_port)
            print(udp_dst_port)
            ovs_dict = {
                "nw_src": getValIfKeyExists(abstract_dict, "ip_src"),
                "nw_dst": getValIfKeyExists(abstract_dict, "ip_dst"),
                "priority": getValIfKeyExists(abstract_dict, "priority"),
                "protocol": getValIfKeyExists(abstract_dict, "protocol"),
                "tcp_src": tcp_src_port,
                "tcp_dst": tcp_dst_port,
                "udp_src": udp_src_port,
                "udp_dst": udp_dst_port,
                "actions": getValIfKeyExists(abstract_dict, "actions")
            }
            return ovs_dict

        def abstract_to_traffic_control_flow(abstract_dict):
            tc_dict = {
                "ip_src": getValIfKeyExists(abstract_dict, "ip_src"),
                "ip_dst": getValIfKeyExists(abstract_dict, "ip_dst"),
                "protocol": getValIfKeyExists(abstract_dict, "protocol"),
                "port_src": getValIfKeyExists(dict_representation, "port_src"),
                "port_dst": getValIfKeyExists(dict_representation, "port_dst"),
                "actions": getValIfKeyExists(abstract_dict, "actions"),
                "rate_limit": getValIfKeyExists(abstract_dict, "rate_limit")
            }
            return tc_dict

        if self.actions is not None:
            if self.actions == "drop":
                self.ovs_flow = OvsFlow()
                ovs_dict = abstract_to_ovs_flow(dict_representation)
                self.ovs_flow.set(ovs_dict)
            elif self.actions == "accept":
                self.traffic_control_flow = TrafficControlFlow()
                traffic_control_dict = abstract_to_traffic_control_flow(dict_representation)
                self.traffic_control_flow.set(traffic_control_dict)

    @property
    def serialize(self):
        serialized_obj = {
                "id": self.id,
                "ip_src": self.ip_src,
                "ip_dst": self.ip_dst,
                "priority": self.priority,
                "protocol": self.protocol,
                "port_src": self.port_src,
                "port_dst": self.port_dst,
                "rate_limit": self.rate_limit,
                "actions": self.actions
        }
        return serialized_obj

    @property
    def serialize_w_title(self):
        serialized_obj = {
            "abstract_flow": self.serialize
        }
        return serialized_obj


    def get_by_filter(self):
        with db_session() as db:
            flows = db.query(AbstractFlow) \
                .filter(AbstractFlow.id == self.id if self.id != None else True) \
                .filter(AbstractFlow.ip_src == self.ip_src if self.ip_src != None else True) \
                .filter(AbstractFlow.ip_dst == self.ip_dst if self.ip_dst != None else True) \
                .filter(AbstractFlow.priority == self.priority if self.priority != None else True) \
                .filter(AbstractFlow.protocol == self.protocol if self.protocol != None else True) \
                .filter(AbstractFlow.port_src == self.port_src if self.port_src != None else True) \
                .filter(AbstractFlow.port_dst == self.port_dst if self.port_dst != None else True) \
                .filter(AbstractFlow.rate_limit == self.rate_limit if self.rate_limit != None else True) \
                .filter(AbstractFlow.actions == self.actions if self.actions != None else True) \
                .all()

            ## Needed if @property is removed - TO investigate why
            flows_dict = []
            for flow in flows:
                print(flow)
                flow_dict = flow.serialize
                flows_dict.append(flow_dict)

            db.commit()

        return flows_dict

    def get_by_filter_obj(self, db):
        flows = db.query(AbstractFlow) \
            .filter(AbstractFlow.id == self.id if self.id != None else True) \
            .filter(AbstractFlow.ip_src == self.ip_src if self.ip_src != None else True) \
            .filter(AbstractFlow.ip_dst == self.ip_dst if self.ip_dst != None else True) \
            .filter(AbstractFlow.priority == self.priority if self.priority != None else True) \
            .filter(AbstractFlow.protocol == self.protocol if self.protocol != None else True) \
            .filter(AbstractFlow.port_src == self.port_src if self.port_src != None else True) \
            .filter(AbstractFlow.port_dst == self.port_dst if self.port_dst != None else True) \
            .filter(AbstractFlow.rate_limit == self.rate_limit if self.rate_limit != None else True) \
            .filter(AbstractFlow.actions == self.actions if self.actions != None else True) \
            .all()
        return flows

    def create_db(self, db):
        # with db_session() as db:
        db.add(self)
        db.flush()
        db.refresh(self)
        return_id = self.id
        return return_id

    def delete_db(self, db):
        temp_obj = db.query(AbstractFlow).get(self.id)
        db.delete(temp_obj)
        db.flush()
