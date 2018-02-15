import helpers.CommandExecutionHelper as CommandExecutionHelper
import pexpect

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, and_
from sqlalchemy.orm import relationship, backref
from models.Base import Base
from helpers.DbHelper import on_connect, db_session
from helpers.CommonHelper import getValIfKeyExists
from configuration import config as cnf

class TrafficControlFlow(Base):
    __tablename__ = 'traffic_control_flow'

    id = Column(Integer, primary_key=True)
    abstract_flow_id = Column(Integer, ForeignKey('abstract_flow.id',
                                                  onupdate="cascade", ondelete="cascade"),
                              nullable=False)

    ip_src = Column(String(16), nullable=True)
    ip_dst = Column(String(16), nullable=True)

    priority = Column(Integer, nullable=True)

    protocol = Column(String(32), nullable=True)
    port_src = Column(Integer, nullable=True)
    port_dst = Column(Integer, nullable=True)
    rate_limit = Column(Integer, nullable=True)

    actions = Column(String(64), nullable=True)


    def __repr__(self):
        return "<TrafficControlFlow(id='%s', ip_src='%s', ip_dst='%s', priority='%s', protocol='%s', port_src='%s', " \
               "port_dst='%s' rate_limit='%s' actions='%s')>" % \
               (self.id, self.ip_src, self.ip_dst, self.priority, self.protocol, self.port_src, self.port_dst,
                self.rate_limit, self.actions)

    def set(self, dict_representation):
        self.id = getValIfKeyExists(dict_representation, "id")
        self.ip_src = getValIfKeyExists(dict_representation, "ip_src")
        self.ip_dst = getValIfKeyExists(dict_representation, "ip_dst")
        self.protocol = getValIfKeyExists(dict_representation, "protocol").lower()
        self.port_src = getValIfKeyExists(dict_representation, "port_src")
        self.port_dst = getValIfKeyExists(dict_representation, "port_dst")
        self.rate_limit = getValIfKeyExists(dict_representation, "rate_limit")
        self.actions = getValIfKeyExists(dict_representation, "actions")

    @property
    def serialize(self):
        serialized_obj = {
                "id": self.id,
                "ip_src": self.ip_src,
                "ip_dst": self.ip_dst,
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
            "traffic_control_flow": self.serialize
        }
        return serialized_obj


    def get_by_filter(self):
        with db_session() as db:
            traffic_control_flows = db.query(TrafficControlFlow) \
                .filter(TrafficControlFlow.id == self.id if self.id != None else True) \
                .filter(TrafficControlFlow.ip_src == self.ip_src if self.ip_src != None else True) \
                .filter(TrafficControlFlow.ip_dst == self.ip_dst if self.ip_dst != None else True) \
                .filter(TrafficControlFlow.protocol == self.protocol if self.protocol != None else True) \
                .filter(TrafficControlFlow.port_src == self.port_src if self.port_src != None else True) \
                .filter(TrafficControlFlow.port_dst == self.port_dst if self.port_dst != None else True) \
                .filter(TrafficControlFlow.rate_limit == self.rate_limit if self.rate_limit != None else True) \
                .filter(TrafficControlFlow.actions == self.actions if self.actions != None else True) \
                .all()

            ## Needed if @property is removed - TO investigate why
            traffic_control_flows_dict = []
            for traffic_control_flow in traffic_control_flows:
                print(traffic_control_flow)
                traffic_control_flow_dict = traffic_control_flow.serialize
                traffic_control_flows_dict.append(traffic_control_flow_dict)

            db.commit()

        return traffic_control_flows_dict

    def apply(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("add")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("TrafficControlFlow created")
        return "True"

    def delete(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("delete")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("TrafficControlFlow deleted")
        return "True"


    def create_db(self, db):
        db.add(self)
        db.flush()
        db.refresh(self)
        return_id = self.id
        return return_id


    def delete_db(self, db):
        temp_obj = db.query(TrafficControlFlow).get(self.id)
        temp_obj.delete()
        db.delete(temp_obj)
        db.flush()


    def generate_flow_command(self, ovs_flow_action):
        command = ""
        if ovs_flow_action == "add":
            command = "tc filter add dev {0} parent ffff: protocol ip prio {1} u32 ".format(cnf.TRAFFIC_CONTROL_IFACE,
                                                                                            self.id)

            if self.protocol == "tcp" or self.protocol == "TCP":
                command = command + "match ip protocol 0x06 0xff "
            elif self.protocol == "udp" or self.protocol == "UDP":
                command = command + "match ip protocol 0x11 0xff "

            if self.port_src is not None:
                command = command + "match ip sport {0} 0xffff ".format(self.port_src)
            if self.port_dst is not None:
                command = command + "match ip dport {0} 0xffff ".format(self.port_dst)

            if self.ip_src is not None:
                command = command + "match ip src {0} ".format(self.ip_src)
            if self.ip_dst is not None:
                command = command + "match ip dst {0} ".format(self.ip_dst)


            command = command + "police rate {0} burst {1} drop flowid :1".format(self.rate_limit,
                                                                                  cnf.TRAFFIC_CONTROL_UNIV_BURST_LIMIT)

        elif ovs_flow_action == "delete":
            command = "tc filter del dev {0} prio {1} parent ffff:".format(cnf.TRAFFIC_CONTROL_IFACE, self.id)

        return command