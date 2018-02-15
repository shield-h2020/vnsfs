import helpers.CommandExecutionHelper as CommandExecutionHelper
import pexpect

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, and_
from sqlalchemy.orm import relationship, backref
from models.Base import Base
from helpers.DbHelper import on_connect, db_session
from helpers.CommonHelper import getValIfKeyExists


def get_current_flows():
    child = pexpect.spawn('ovs-ofctl dump-flows br0')
    child.expect(pexpect.EOF)
    string_rules = child.before.decode("utf-8")
    string_rules = string_rules.split("\n")
    # print(string_rules)
    ovs_rules = []

    if not isinstance(string_rules, str):
        for line in string_rules:
            if line.startswith("ovs-ofctl", 0, len(line)):
                print(line)
                return "ERROR!"

            if not line.startswith("NXST_FLOW", 0, len(line)):

                # String before "action" ##############
                actions_num = line.find("actions")
                if not actions_num == -1:
                    line_before_actions = line[:line.find("actions")]
                else:
                    line_before_actions = line

                all_fields_ba = line_before_actions.split(",")
                ovs_rule = {}
                # print(all_fields)
                for field in all_fields_ba:
                    key_val_pair = field.split("=")
                    # print(key_val_pair)
                    if len(key_val_pair) > 1:
                        key = key_val_pair[0]
                        val = key_val_pair[1]
                        key = key.strip()
                        val = val.strip()
                        ovs_rule[key] = val

                # String after "action" ##############
                rule_actions = []
                if not actions_num == -1:
                    line_after_actions = line[line.find("actions") + 8:]
                    all_fields_aa = line_after_actions.split(",")
                    for field in all_fields_aa:
                        # if not field.find(":") == -1:
                        key_val_pair = field.split(":")
                        if len(key_val_pair) > 1:
                            key = key_val_pair[0]
                            val = key_val_pair[1]
                            key = key.strip()
                            val = val.strip()
                            action_dict = dict()
                            action_dict[key] = val.rstrip()
                            rule_actions.append(action_dict)
                        else:
                            val = key_val_pair[0]
                            action_str = val.rstrip()
                            rule_actions.append(action_str)

                if 'cookie' not in ovs_rule:
                    continue

                ovs_rule["actions"] = rule_actions
                ovs_rules.append(ovs_rule)

    return ovs_rules

class Flow(Base):
    __tablename__ = 'flow'

    id = Column(Integer, primary_key=True)
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
        return "<Flow(id='%s', nw_src='%s', nw_dst='%s', n_packets='%s', n_bytes='%s', cookie='%s', idle_age='%s', " \
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

    @property
    def serialize_w_title(self):
        serialized_obj = {
            "flow": self.serialize
        }
        return serialized_obj


    def get_by_filter(self):
        with db_session() as db:
            flows = db.query(Flow) \
                .filter(Flow.id == self.id if self.id != None else True) \
                .filter(Flow.nw_src == self.nw_src if self.nw_src != None else True) \
                .filter(Flow.nw_dst == self.nw_dst if self.nw_dst != None else True) \
                .filter(Flow.cookie == self.cookie if self.cookie != None else True) \
                .filter(Flow.priority == self.priority if self.priority != None else True) \
                .filter(Flow.table == self.table if self.table != None else True) \
                .filter(Flow.protocol == self.protocol if self.protocol != None else True) \
                .filter(Flow.tcp_src == self.tcp_src if self.tcp_src != None else True) \
                .filter(Flow.tcp_dst == self.tcp_dst if self.tcp_dst != None else True) \
                .filter(Flow.udp_src == self.udp_src if self.udp_src != None else True) \
                .filter(Flow.udp_dst == self.udp_dst if self.udp_dst != None else True) \
                .all()

            ## Needed if @property is removed - TO investigate why
            flows_json = []
            for flow in flows:
                print(flow)
                flow_json = flow.serialize
                flows_json.append(flow_json)

            db.commit()

        return flows_json

    def apply(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("add")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("Flow created")
        return "True"

    def delete(self):
        ceh = CommandExecutionHelper.CommandExecutionHelper()
        command = self.generate_flow_command("delete")
        print(command)
        result = ceh.execute(command)
        print(result)
        print("Flow deleted")
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

    # def delete_all(self):
    #     ceh = CommandExecutionHelper.CommandExecutionHelper()
    #     command = 'ovs-ofctl del-flows br0'
    #     result = ceh.execute(command)
    #     print(result)
    #     print("Flows deleted")
    #     return "True"

    def create_db(self, db):
        # with db_session() as db:
        db.add(self)
        db.flush()
        db.refresh(self)
        return_id = self.id
        return return_id


    def delete_db(self, db):
        temp_obj = db.query(Flow).get(self.id)
        temp_obj.delete()
        db.delete(temp_obj)
        db.flush()
