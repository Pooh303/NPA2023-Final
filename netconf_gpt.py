from ncclient import manager
import xmltodict

# Connect to the router using NETCONF
m = manager.connect(
    host="192.168.150.140",  # Replace with your router's IP address
    port=830,                # Replace with your NETCONF port number (default is 830)
    username="admin",        # Replace with your router's username
    password="cisco",        # Replace with your router's password
    hostkey_verify=False     # Disable host key verification for testing (use cautiously)
)

def create():
    # Replace with the actual YANG configuration data to create a resource (e.g., loopback interface)
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback100</name>
                <description>Test Loopback</description>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface created successfully."
    except:
        print("Error during create operation!")

def delete():
    # Replace with YANG data to delete the resource (e.g., loopback interface)
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback100</name>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface deleted successfully."
    except:
        print("Error during delete operation!")

def enable():
    # Replace with YANG data to enable an interface
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet2</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface enabled successfully."
    except:
        print("Error during enable operation!")

def disable():
    # Replace with YANG data to disable an interface
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet2</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface disabled successfully."
    except:
        print("Error during disable operation!")

def netconf_edit_config(netconf_config):
    # Replace with the correct NETCONF edit-config operation targeting the 'running' datastore
    return m.edit_config(target="running", config=netconf_config)

def status():
    # Define a NETCONF filter to retrieve operational state of the interface
    netconf_filter = """
    <filter>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet2</name>
            </interface>
        </interfaces-state>
    </filter>
    """

    try:
        # Use the 'get' operation to fetch the status of the interface
        netconf_reply = m.get(filter=netconf_filter)
        print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # Check if the interface status is present
        if 'interfaces-state' in netconf_reply_dict:
            interface = netconf_reply_dict['interfaces-state']['interface']
            admin_status = interface['admin-status']
            oper_status = interface['oper-status']

            if admin_status == 'up' and oper_status == 'up':
                return "Interface is up and operational."
            elif admin_status == 'down' and oper_status == 'down':
                return "Interface is down."
        else:
            return "No operational state data for the interface."
    except:
        print("Error during status retrieval!")
