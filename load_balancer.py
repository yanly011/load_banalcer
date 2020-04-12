# -*- coding: utf-8 -*-

import acos_client as acos
import configparser
import os
import argparse


def print_group_info(group_json):
    print("Group Name: " + group_json['name'])
    print("Group protocol: " + group_json['protocol'])
    print("UUID: " + group_json['uuid'])
    servers_list_in_group = group_json['member-list']
    print("Member List:")
    for i, server in enumerate(servers_list_in_group):
        print("--Server " + str(i + 1))
        print("    Server Name: " + server['name'])
        print("    Server Port: " + str(server['port']))
        print("    Server State: " + server['member-state'])
        print("    Server UUID: " + server['uuid'])
        print("    Server URL: " + server['a10-url'])


def print_server_info(server_json):
    print("Server Name: " + server_json['name'])
    print("Server Host: " + str(server_json['host']))
    print("Server State: " + server_json['action'])
    print("Server UUID: " + server_json['uuid'])
    print("stats-data-action: " + server_json['stats-data-action'])
    print("Port List: ")
    port_list = server_json['port-list']
    for index, port in enumerate(port_list):
        print("--Port " + str(index + 1))
        print("    Port Number: " + str(port['port-number']))
        print("    Protocol: " + port['protocol'])
        print("    Range: " + str(port['range']))
        print("    State: " + port['action'])
        print("    SSL: " + str(port['no-ssl']))
        print("    Connection Limit: " + str(port['conn-limit']))
        print("    No Logging: " + str(port['no-logging']))
        print("    UUID: " + port['uuid'])
        print("    URL: " + port['a10-url'])


def list_service_group(acos_lient, group_name):
    if group_name == 'all':
        group_list = []
        try:
            json_string = acos_lient.slb.service_group.all()
            group_list = json_string['service-group-list']
        except Exception as e:
            print("Sorry, cannot find any service group... The error message is: " + str(e))
        if len(group_list) == 0:
            print("Sorry, cannot find any service group...")
        else:
            for index, group in enumerate(group_list):
                print('-----------Service Group ' + str(index + 1)+'-------------------')
                print_group_info(group)
                print('\n')
    else:
        try:
            json_string = acos_lient.slb.service_group.get(group_name)
        except Exception as e:
            print("Cannot get the information of the group " + group_name + ". The error message is: " + str(e))
            return
        if 'service-group' in json_string:
            group = json_string['service-group']
            print_group_info(group)
        else:
            print("Sorry, cannot find the service group...")


def list_servers(acos_lient, status):
    try:
        json_string = acos_lient.slb.service_group.all()
        group_list = json_string['service-group-list']
    except Exception as e:
        print("Sorry, cannot get the information of service group, the error message is: " + str(e))
        return
    server_list = []
    if len(group_list) == 0:
        print("Sorry, cannot find any service group...")
    else:
        for group in group_list:
            servers_list_in_group = group['member-list']
            for server in servers_list_in_group:
                try:
                    server_json = acos_lient.slb.server.get(server['name'])
                    server_info = server_json['server']
                    server_list.append(server_info)
                except Exception as e:
                    print('Sorry, cannot get the information of the server belongs to the group of ' + group['name'])
                    print('The error message is: ' + str(e))
                    continue
        if len(server_list) > 0:
            if status == 'all':
                for i, server in enumerate(server_list):
                    print("--Server "+str(i+1))
                    print_server_info(server)
            else:
                for i, server in enumerate(server_list):
                    if server['action'] == status:
                        print("--Server "+str(i+1))
                        print_server_info(server)


def show_server_info(acos_lient, server_name):
    try:
        json_string = acos_lient.slb.server.get(server_name)
    except Exception as e:
        print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
        return
    if 'server' in json_string:
        server = json_string['server']
        print_server_info(server)
    else:
        print("Sorry, cannot find the server...")


def enable_server(acos_lient, server_name, ip_address):
    try:
        json_string = acos_lient.slb.server.get(server_name)
    except Exception as e:
        print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
        return

    server = json_string['server']
    if server['action'] == 'enable':
        print('This server is enabled already...')
        return
    if ip_address != server['host']:
        print('Incorrect ip address, please check it...')
        return
    else:
        try:
            result = acos_lient.slb.server.update(server_name, ip_address)
            server = result['server']
            if server['action'] == 'enable':
                print("Success to enable the server of: " + server_name)
            else:
                print("Failed to enable the server of " + server_name + ', please try again')
        except Exception as e:
            print("Cannot enable the server of: " + server_name + ". The error message is: " + str(e))


def enable_all_servers(acos_lient):
    try:
        json_string = acos_lient.slb.service_group.all()
        group_list = json_string['service-group-list']
    except Exception as e:
        print("Sorry, cannot get the information of service group, the error message is: " + str(e))
        return
    server_list = []
    if len(group_list) == 0:
        print("Sorry, cannot find any service group...")
    else:
        for group in group_list:
            servers_list_in_group = group['member-list']
            for server in servers_list_in_group:
                try:
                    server_json = acos_lient.slb.server.get(server['name'])
                    server_info = server_json['server']
                    server_list.append(server_info)
                except Exception as e:
                    print('Sorry, cannot get the information of the server belongs to the group of ' + group['name'])
                    print('The error message is: ' + str(e))
                    continue
        if len(server_list) > 0:
            for server in server_list:
                if server['action'] == 'disable':
                    print("Enable the Server: " + server['name'])
                    try:
                        enable_server(acos_lient, server['name'], server['host'])
                    except Exception as e:
                        print(str(e))
                        continue


def disable_server(acos_lient, server_name, ip_address):
    try:
        json_string = acos_lient.slb.server.get(server_name)
    except Exception as e:
        print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
        return

    server = json_string['server']
    if server['action'] == 'disable':
        print('This server is disabled already...')
        return
    if ip_address != server['host']:
        print('Incorrect ip address, please check it...')
        return
    else:
        try:
            result = acos_lient.slb.server.update(server_name, ip_address, status=0)
            server = result['server']
            if server['action'] == 'disable':
                print("Success to disable the server of: " + server_name)
            else:
                print("Failed to disable the server of " + server_name + ', please try again')

        except Exception as e:
            print("Cannot disable the server of: " + server_name + ". The error message is: " + str(e))


def main():
    config = configparser.ConfigParser()
    module_path = os.path.dirname(__file__)
    filename = os.path.join(module_path, 'load_balancer.conf')
    config.read(filename)

    host_name = config.get('test', 'a10_domain')
    admin_name = config.get('test', 'a10_admin_name')
    admin_pass = config.get('test', 'a10_admin_passport')

    try:
        c = acos.Client(host_name, acos.AXAPI_30, admin_name, admin_pass)
    except Exception as e:
        print('Http request error: ' + str(e.message))
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("-lg", '--groupName', help="List all service group or one group")
    parser.add_argument("-ls", '--status', help="List servers according to state")
    parser.add_argument("-ss", '--serverName', help="Show a server's information")
    parser.add_argument("-es", "--disabledServerName", "--disabledServerIP", help="Enable a server")
    parser.add_argument("-ds", "--enabledServerName", "--enabledServerIP", help="Disable a server")
    parser.add_argument("-ip", "--ipAddress", help="Ip address of server")

    args = parser.parse_args()
    if args.groupName:
        list_service_group(c, args.groupName)
    if args.status:
        list_servers(c, args.status)
    if args.serverName:
        show_server_info(c, args.serverName)
    if args.disabledServerName and args.ipAddress:
        enable_server(c, args.disabledServerName, args.ipAddress)
    if args.enabledServerName and args.ipAddress:
        disable_server(c, args.enabledServerName, args.ipAddress)
    if args.disabledServerName == 'all':
        enable_all_servers(c)


if __name__ == '__main__':
    main()
