from ncclient import manager
import xmltodict
import xml.dom.minidom

# Connect to the router using NETCONF
m = manager.connect(
    host="192.168.20.158",  # Replace with your router's IP address
    port=830,                # Replace with your NETCONF port number (default is 830)
    username="admin",        # Replace with your router's username
    password="cisco",        # Replace with your router's password
    hostkey_verify=False     # Disable host key verification for testing (use cautiously)
)

def create(name):
    # Replace with the actual YANG configuration data to create a resource (e.g., loopback interface)
    netconf_loopback = f"""
        <config>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
        <Loopback>
            <name>{name}</name>
            <description>Loopback{name}</description>
            <ip>
            <address>
            <primary>
            <address>172.30.182.1</address>
            <mask>255.255.255.0</mask>
            </primary>
            </address>
            </ip>
        </Loopback>
        </interface>
        </native>
        </config>
        """
    
    # netconf_reply = m.edit_config(target="running", config=netconf_loopback)
    # print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())
    if status(name) == f"Interface Loopback {name} is enabled" or status(name) == f"Interface Loopback {name} is disabled":
        return f"Cannot create: Interface loopback {name}"
    try:
        netconf_reply = netconf_edit_config(netconf_loopback)
        xml_data = netconf_reply.xml
        # print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {name} is created successfully"
    except Exception as e:
        return f"An error occurred: {e}"
    

def delete(name):
    # Replace with YANG data to delete the resource (e.g., loopback interface)
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback{name}</name>
            </interface>
        </interfaces>
    </config>
    """

    if status(name) != f"Interface Loopback {name} is enabled" and status(name) != f"Interface Loopback {name} is disabled":
        return f"Cannot delete: Interface loopback {name}"
    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        # print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {name} is deleted successfully"
    except Exception as e:
        return f"An error occurred: {e}"

def enable(name):
    # Replace with YANG data to enable an interface
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{name}</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    if status(name) != f"Interface Loopback {name} is enabled" and status(name) != f"Interface Loopback {name} is disabled":
        return f"Cannot delete: Interface loopback {name}"
    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        # print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {name} is enabled successfully"
    except Exception as e:
        return f"An error occurred: {e}"

def disable(name):
    # Replace with YANG data to disable an interface
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{name}</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """

    if status(name) != f"Interface Loopback {name} is enabled" and status(name) != f"Interface Loopback {name} is disabled":
        return f"Cannot delete: Interface loopback {name}"
    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        # print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {name} is shutdowned successfully"
    except Exception as e:
        return f"An error occurred: {e}"

def status(name):
    # Define a NETCONF filter to retrieve operational state of the interface
    netconf_filter = f"""
    <filter>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{name}</name>
            </interface>
        </interfaces-state>
    </filter>
    """

    try:
        # Use the 'get' operation to fetch the status of the interface
        netconf_reply = m.get(filter=netconf_filter)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)
        data = netconf_reply_dict.get('rpc-reply', {}).get('data', {})
        interfaces_state = ""

        # Check if the interface status is present
        if data :
            interfaces_state = data.get('interfaces-state')

        # print(interfaces_state)
            
        if 'interface' in interfaces_state:
            interface = interfaces_state['interface']
            admin_status = interface.get('admin-status')
            oper_status = interface.get('oper-status')
            
            # print(admin_status, oper_status)

            if admin_status == 'up' and oper_status == 'up':
                return f"Interface Loopback {name} is enabled"
            elif admin_status == 'down' and oper_status == 'down':
                return f"Interface Loopback {name} is disabled"
            else:
                return f"Interface Loopback {name} has inconsistent states."
        else:
            return f"No Interface Loopback {name}"

    except Exception as e:     
        return f"An error occurred: {e}"

def netconf_edit_config(netconf_config):
    # Replace with the correct NETCONF edit-config operation targeting the 'running' datastore
    return m.edit_config(target="running", config=netconf_config)