vnfd-catalog:
    vnfd:
    -   description: Layer 3 Filter implementation using iptables
        id: l3filter_vnfd
        logo: ubuntu-logo14.png
        mgmt-interface:
            vdu-id: l3filter_vdu
        name: l3filter_vnfd
        connection-point:
        -   name: eth0
            type: VPORT
        -   name: eth1
            type: VPORT
        -   name: eth2
            type: VPORT

        service-function-chain: UNAWARE
        short-name: l3filter
        vdu:
        -   cloud-init-file: cloud_init.cfg
            count: '1'
            description: l3filter-VM
            guest-epa:
                cpu-pinning-policy: ANY
            id: l3filter_vdu
            image: ubuntu
            interface:
            -   external-connection-point-ref: eth0
                name: eth0
                position: '1'
                virtual-interface:
                    type: OM-MGMT
            -   external-connection-point-ref: eth1
                name: eth1
                position: '2'
                virtual-interface:
                    type: VIRTIO
            -   external-connection-point-ref: eth2
                name: eth2
                position: '3'
                virtual-interface:
                    type: VIRTIO
            name: l3filter_vdu
            vm-flavor:
                memory-mb: '256'
                storage-gb: '4'
                vcpu-count: '1'
        vendor: POLITO
        version: '1.0'
        vnf-configuration:
            config-attributes:
                config-delay: 1
            config-primitive:
            -   name: start
            -   name: stop
            -   name: restart
            -   name: config
                parameter:
                -   data-type: STRING
                    default-value: <rw_mgmt_ip>
                    name: ssh-hostname
                -   data-type: STRING
                    default-value: ubuntu
                    name: ssh-username
                -   data-type: STRING
                    default-value: osm4u
                    name: ssh-password
                -   data-type: STRING
                    default-value: 9999
                    name: rest-api-port
            -   name: set-policies
                parameter:
                -   data-type: STRING
                    default-value: ""
                    name: policies
            -   name: get-policies
            -   name: delete-policy
                parameter:
                -   data-type: INTEGER
                    default-value: 1
                    name: policy
            -   name: delete-policies
            initial-config-primitive:
            -   name: config
                parameter:
                -   name: ssh-hostname
                    value: <rw_mgmt_ip>
                -   name: ssh-username
                    value: ubuntu
                -   name: ssh-password
                    value: osm4u
                -   name: rest-api-port
                    value: 9999
                seq: '1'
            -   name: start
                seq: '2'
            juju:
                charm: l3filter
