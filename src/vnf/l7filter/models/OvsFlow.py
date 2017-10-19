import helpers.CommandExecutionHelper as CommandExecutionHelper
import pexpect

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, and_
from sqlalchemy.orm import relationship, backref
from models.Base import Base
from helpers.DbHelper import on_connect, db_session
from helpers.CommonHelper import getValIfKeyExists


class OvsFlow(Base):
    __tablename__ = 'ovs_flow'

    id = Column(Integer, primary_key=True)

    # abstract_flow_id = Column(Integer, ForeignKey('abstract_flow.id',
    #                                               onupdate="cascade", ondelete="cascade"),
    #                           nullable=False)

    # TODO: Just temporary solution abstract flow id must never be null
    abstract_flow_id = Column(Integer, ForeignKey('abstract_flow.id',
                                                  onupdate="cascade", ondelete="cascade"),
                              nullable=True)

    nw_src = Column(String(16), nullable=True)
    nw_dst = Column(String(16), nullable=True)

    n_packets = Column(Integer, nullable=True)
    n_bytes = Column(Integer, nullable=True)

    cookie = Column(String(32), nullable=True)

    idle_age = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    table = Column(Integer, nullable=True)

    protocol = Column(String(32), nullable=True)
    tcp_src = Column(Integer, nullable=True)
    tcp_dst = Column(Integer, nullable=True)

    udp_src = Column(Integer, nullable=True)
    udp_dst = Column(Integer, nullable=True)

    actions = Column(String(64), nullable=True)


    def __repr__(self):
        return "<OvsFlow(id='%s', nw_src='%s', nw_dst='%s', n_packets='%s', n_bytes='%s', cookie='%s', idle_age='%s', " \
               "duration='%s', priority='%s', table='%s', protocol='%s', tcp_src='%s', tcp_dst='%s', udp_src='%s', " \
               "udp_dst='%s', actions='%s')>" % \
               (self.id, self.nw_src, self.nw_dst, self.n_packets, self.n_bytes, self.cookie, self.idle_age,
                self.duration, self.priority, self.table, self.protocol, self.tcp_src, self.tcp_dst, self.udp_src,
                self.udp_dst, self.actions)

    def set(self, dict_representation):

        self.id = getValIfKeyExists(dict_representation, "id")
        self.nw_src = getValIfKeyExists(dict_representation, "nw_src")
        self.nw_dst = getValIfKeyExists(dict_representation, "nw_dst")
        self.n_packets = getValIfKeyExists(dict_representation, "n_packets")
        self.n_bytes = getValIfKeyExists(dict_representation, "n_bytes")
        self.cookie = getValIfKeyExists(dict_representation, "cookie")
        self.idle_age = getValIfKeyExists(dict_representation, "idle_age")
        self.duration = getValIfKeyExists(dict_representation, "duration")
        self.priority = getValIfKeyExists(dict_representation, "priority")
        self.table = getValIfKeyExists(dict_representation, "table")
        self.protocol = getValIfKeyExists(dict_representation, "protocol").lower()
        self.tcp_src = getValIfKeyExists(dict_representation, "tcp_src")
        self.tcp_dst = getValIfKeyExists(dict_representation, "tcp_dst")
        self.udp_src = getValIfKeyExists(dict_representation, "udp_src")
        self.udp_dst = getValIfKeyExists(dict_representation, "udp_dst")
        self.actions = getValIfKeyExists(dict_representation, "actions")

    @property
    def serialize(self):
        serialized_obj = {
                "id": self.id,
                "nw_src": self.nw_src,
                "nw_dst": self.nw_dst,
                "n_packets": self.n_packets,
                "n_bytes": self.n_bytes,
                "cookie": self.cookie,
                "idle_age": self.idle_age,
                "duration": self.duration,
                "priority": self.priority,
                "table": self.table,
                "protocol": self.protocol,
                "tcp_src": self.tcp_src,
                "tcp_dst": self.tcp_dst,
                "udp_src": self.udp_src,
                "udp_dst": self.udp_dst,
                "actions": self.actions
        }
        return serialized_obj


    def abstract_to_ovs_flow(self, abstract_dict):
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

    @property
    def serialize_as_abstract(self):
        port_src = None
        port_dst = None
        if self.protocol.lower() == "tcp":
            print("*********************TCP************************")
            port_src = self.tcp_src
            port_dst = self.tcp_dst
        elif self.protocol.lower() == "udp":
            print("*********************UDP************************")
            port_src = self.udp_src
            port_dst = self.udp_dst

        serialized_obj = {
                "id": self.id,
                "ip_src": self.nw_src,
                "ip_dst": self.nw_dst,
                "priority": self.priority,
                "protocol": self.protocol,
                "port_src": port_src,
                "port_dst": port_dst,
                "rate_limit": None,
                "actions": self.actions
        }
        return serialized_obj


    @property
    def serialize_w_title(self):
        serialized_obj = {
            "ovs_flow": self.serialize
        }
        return serialized_obj


    def get_by_filter(self, transform_to_abstract_flow=False):
        with db_session() as db:
            flows = db.query(OvsFlow) \
                .filter(OvsFlow.id == self.id if self.id != None else True) \
                .filter(OvsFlow.nw_src == self.nw_src if self.nw_src != None else True) \
                .filter(OvsFlow.nw_dst == self.nw_dst if self.nw_dst != None else True) \
                .filter(OvsFlow.cookie == self.cookie if self.cookie != None else True) \
                .filter(OvsFlow.priority == self.priority if self.priority != None else True) \
                .filter(OvsFlow.table == self.table if self.table != None else True) \
                .filter(OvsFlow.protocol == self.protocol if self.protocol != None else True) \
                .filter(OvsFlow.tcp_src == self.tcp_src if self.tcp_src != None else True) \
                .filter(OvsFlow.tcp_dst == self.tcp_dst if self.tcp_dst != None else True) \
                .filter(OvsFlow.udp_src == self.udp_src if self.udp_src != None else True) \
                .filter(OvsFlow.udp_dst == self.udp_dst if self.udp_dst != None else True) \
                .all()

            #TODO: Needed if @property is removed - TO investigate why
            flows_json = []
            if transform_to_abstract_flow is False:
                for flow in flows:
                    # print(flow)
                    flow_json = flow.serialize
                    flows_json.append(flow_json)
            else:
                for flow in flows:
                    flow_json = flow.serialize_as_abstract
                    print(flow_json)
                    flows_json.append(flow_json)


            db.commit()

        return flows_json

    def get_by_filter_obj(self, db):
        flows = db.query(OvsFlow) \
            .filter(OvsFlow.id == self.id if self.id != None else True) \
            .filter(OvsFlow.nw_src == self.nw_src if self.nw_src != None else True) \
            .filter(OvsFlow.nw_dst == self.nw_dst if self.nw_dst != None else True) \
            .filter(OvsFlow.cookie == self.cookie if self.cookie != None else True) \
            .filter(OvsFlow.priority == self.priority if self.priority != None else True) \
            .filter(OvsFlow.table == self.table if self.table != None else True) \
            .filter(OvsFlow.protocol == self.protocol if self.protocol != None else True) \
            .filter(OvsFlow.tcp_src == self.tcp_src if self.tcp_src != None else True) \
            .filter(OvsFlow.tcp_dst == self.tcp_dst if self.tcp_dst != None else True) \
            .filter(OvsFlow.udp_src == self.udp_src if self.udp_src != None else True) \
            .filter(OvsFlow.udp_dst == self.udp_dst if self.udp_dst != None else True) \
            .all()
        return flows


    def apply(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("add")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("OvsFlow created")
        return "True"

    def delete(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("delete")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("OvsFlow deleted")
        return "True"


    def generate_flow_command(self, ovs_flow_action):
        command = ""
        if ovs_flow_action == "add":
            command = "ovs-ofctl add-flow br0 "

        if ovs_flow_action == "delete":
            command = "ovs-ofctl del-flows --strict br0 "

        if self.priority is not None:
            command = command + "priority={0},".format(self.priority)

        if self.protocol == "tcp" or self.protocol == "TCP":
            command = command + "tcp"
            if self.tcp_src is not None:
                command = command + ",tcp_src={0}".format(self.tcp_src)
            if self.tcp_dst is not None:
                command = command + ",tcp_dst={0}".format(self.tcp_dst)
        elif self.protocol == "udp" or self.protocol == "UDP":
            command = command + "udp"
            if self.udp_src is not None:
                command = command + ",udp_src={0}".format(self.udp_src)
            if self.udp_dst is not None:
                command = command + ",udp_dst={0}".format(self.udp_dst)
        else:
            command = command + "ip"

        # print(self.nw_src)
        if self.nw_src is not None:
            command = command + ",nw_src={0}".format(self.nw_src)
        if self.nw_dst is not None:
            command = command + ",nw_dst={0}".format(self.nw_dst)


        if ovs_flow_action == "add":
            command = command + ",actions=drop"

        return command

    def create_db(self, db):
        # with db_session() as db:
        db.add(self)
        db.flush()
        db.refresh(self)
        return_id = self.id
        return return_id

    def delete_db(self, db):
        temp_obj = db.query(OvsFlow).get(self.id)
        temp_obj.delete()
        db.delete(temp_obj)
        db.flush()
