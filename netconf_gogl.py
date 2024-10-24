from ncclient import manager
import xmltodict
import re

# NETCONF connection details (replace with your actual credentials)
m = manager.connect(
    host="192.168.20.158",
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False  # Use with caution in production
)

def handle_command(command_string):
    match = re.match(r"/(\d+) (\w+)", command_string)
    if not match:
        return "Invalid command format. Use /<studentID> <command>"

    student_id = match.group(1)
    command = match.group(2)
    loopback_name = student_id
    loopback_ip = f"172.30.{student_id[-3:]}.1"

def format_result_message(result, action, loopback_name):
    if result == "success":
        return f"Interface loopback {loopback_name} is {action} successfully"
    elif result == "failed":
        return f"Error: Failed to {action} interface loopback {loopback_name}"
    else:
        return result  # Return the raw error message if not "success" or "failed"


def create(name, ip_address):
    config = f"""
        <config>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                    <Loopback>
                        <name>{name}</name>
                        <description>Loopback{name}</description>
                        <ip>
                            <address>
                                <primary>
                                    <address>{ip_address}</address>
                                    <mask>255.255.255.0</mask>
                                </primary>
                            </address>
                        </ip>
                    </Loopback>
                </interface>
            </native>
        </config>
    """
    try:
        reply = m.edit_config(target="running", config=config)
        return f"Interface loopback {name} is created successfully" if "<ok/>" in reply.xml else "failed" # Check for <ok/> in the reply
    except Exception as e:
        return str(e)  # Return the error as a string


def delete(name):
    config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback{name}</name>
            </interface>
        </interfaces>
    </config>
    """
    try:
        reply = m.edit_config(target="running", config=config)
        return f"Interface loopback {name} is deleted successfully" if "<ok/>" in reply.xml else "failed"
    except Exception as e:
        return str(e)


def enable(name):  # Corrected: Use "no shutdown" (operation="delete")
    config = f"""
        <config>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                    <Loopback>
                        <name>{name}</name>
                        <shutdown operation="delete"/>
                    </Loopback>
                </interface>
            </native>
        </config>
    """
    try:
        reply = m.edit_config(target="running", config=config)
        return f"Interface loopback {name} is enabled successfully" if "<ok/>" in reply.xml else "failed"
    except Exception as e:
        return str(e)


def disable(name): # Corrected: Use shutdown
    config = f"""
        <config>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                    <Loopback>
                        <name>{name}</name>
                        <shutdown/>
                    </Loopback>
                </interface>
            </native>
        </config>
    """
    try:
        reply = m.edit_config(target="running", config=config)
        return f"Interface loopback {name} is shutdowned successfully" if "<ok/>" in reply.xml else "failed"
    except Exception as e:
        return str(e)

def status(name):
    filter = f"""
        <filter>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                    <Loopback>
                        <name>{name}</name>
                    </Loopback>
                </interface>
            </native>
        </filter>
    """
    try:
        reply = m.get(filter=filter).data_xml # Use data_xml for easier parsing
        data = xmltodict.parse(reply)['rpc-reply']['data']['native']['interface']['Loopback']

        if 'ip' in data and 'address' in data['ip']:
            admin_status = data.get('shutdown') is None  # Check for presence of shutdown
            oper_status = data['ip']['address']['primary'].get('oper-status', 'unknown') # Get oper-status, default to "unknown"
            if admin_status and oper_status == 'up': # check both admin and operational status
                return f"Interface loopback {name} is enabled"
            elif not admin_status and oper_status != 'up': # check both admin and operational status
                return f"Interface loopback {name} is disabled"
            else: 
                 return f"Interface loopback {name} is in an indeterminate state." #admin and operational status don't match

        else:
            return f"Interface loopback {name} has no IP address configured or incomplete data."  # Handle missing or incomplete data

    except Exception as e:
        return f"Error retrieving status: {e}"



def interface_exists(name):
    filter = f"""
        <filter>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                    <Loopback>
                        <name>{name}</name>
                    </Loopback>
                </interface>
            </native>
        </filter>
    """
    try:
        response = m.get(filter=filter)
        return bool(response.data)
    except:
        return False
