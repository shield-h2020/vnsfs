from models.Flow import get_current_flows


class Global:

    def __init__(self, fw_status=True):
        self.fw_status = fw_status
        self.current_flow_list = []

        # for flow in get_current_flows():
        #     if "drop" in flow["actions"]:
        #         self.current_flow_list.append((flow["nw_src"], flow["nw_dst"]))


