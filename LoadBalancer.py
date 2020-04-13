# -*- coding: utf-8 -*-
import acos_client as acos
import configparser
import os
import argparse


class LoadBalancer():
    @staticmethod
    def get_acos_lient(admin, password):
        config = configparser.ConfigParser()
        module_path = os.path.dirname(__file__)
        filename = os.path.join(module_path, 'load_balancer.conf')
        config.read(filename)

        host_name = config.get('test', 'a10_domain')
        version = config.get('test', 'acos_version')
        admin_name = admin
        admin_pass = password

        try:
            if version == '3.0':
                return acos.Client(host_name, acos.AXAPI_30, admin_name, admin_pass)
            else:
                return acos.Client(host_name, acos.AXAPI_21, admin_name, admin_pass)
        except Exception as e:
            print('Http request error: ' + str(e))

    @staticmethod
    def print_group_info(group_json):
        print("Group Name: " + (group_json['name'] if 'name' in group_json else ''))
        print("Group protocol: " + (group_json['protocol']) if 'protocol' in group_json else '')
        print("UUID: " + (group_json['uuid'] if 'uuid' in group_json else ''))
        if 'member-list' in group_json:
            servers_list_in_group = group_json['member-list']
            print("Member List:")
            for i, server in enumerate(servers_list_in_group):
                print("--Server " + str(i + 1))
                print("    Server Name: " + (server['name'] if 'name' in server else ''))
                print("    Server Port: " + str(server['port'] if 'port' in server else ''))
                print("    Server State: " + (server['member-state'] if 'member-state' in server else ''))
                print("    Server UUID: " + (server['uuid'] if 'uuid' in server else ''))
                print("    Server URL: " + (server['a10-url'] if 'a10-url' in server else ''))

    @staticmethod
    def print_server_info(server_json):
        print("Server Name: " + (server_json['name'] if 'name' in server_json else ''))
        print("Server Host: " + str(server_json['host'] if 'host' in server_json else ''))
        print("Server State: " + (server_json['action'] if 'action' in server_json else ''))
        print("Server UUID: " + (server_json['uuid'] if 'uuid' in server_json else ''))
        if 'port-list' in server_json:
            print("Port List: ")
            port_list = server_json['port-list']
            for index, port in enumerate(port_list):
                print("--Port " + str(index + 1))
                print("    Port Number: " + str(port['port-number'] if 'port-number' in port else ''))
                print("    Protocol: " + (port['protocol'] if 'protocol' in port else ''))
                print("    Range: " + str(port['range'] if 'range' in port else ''))
                print("    State: " + (port['action'] if 'action' in port else ''))
                print("    SSL: " + str(port['no-ssl'] if 'no-ssl' in port else ''))
                print("    Connection Limit: " + str(port['conn-limit'] if 'conn-limit' in port else ''))
                print("    No Logging: " + str(port['no-logging'] if 'no-logging' in port else ''))
                print("    UUID: " + (port['uuid'] if 'uuid' in port else ''))
                print("    URL: " + (port['a10-url'] if 'a10-url' in port else ''))

    def list_service_group(self, group_name, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        if group_name == 'all':
            group_list = []
            try:
                json_string = c.slb.service_group.all()
                group_list = json_string['service-group-list'] if 'service-group-list' in json_string else ''
            except Exception as e:
                print("Sorry, cannot find any service group... The error message is: " + str(e))
            if len(group_list) == 0:
                print("Sorry, cannot find any service group...")
            else:
                for index, group in enumerate(group_list):
                    print('-----------Service Group ' + str(index + 1)+'-------------------')
                    self.print_group_info(group)
                    print('\n')
        else:
            try:
                json_string = c.slb.service_group.get(group_name)
            except Exception as e:
                print("Cannot get the information of the group " + group_name + ". The error message is: " + str(e))
                return
            if 'service-group' in json_string:
                group = json_string['service-group']
                self.print_group_info(group)
            else:
                print("Sorry, cannot find the service group...")

    def list_servers(self, status, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        try:
            json_string = c.slb.service_group.all()
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
                        server_json = c.slb.server.get(server['name'])
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
                        self.print_server_info(server)
                else:
                    for i, server in enumerate(server_list):
                        if server['action'] == status:
                            print("--Server "+str(i+1))
                            self.print_server_info(server)

    def show_server_info(self, server_name, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        try:
            json_string = c.slb.server.get(server_name)
        except Exception as e:
            print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
            return
        if 'server' in json_string:
            server = json_string['server']
            self.print_server_info(server)
        else:
            print("Sorry, cannot find the server...")

    def enable_server(self, server_name, ip_address, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        try:
            json_string = c.slb.server.get(server_name)
        except Exception as e:
            print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
            return "Cannot get the information of the server"

        server = json_string['server']
        if server['action'] == 'enable':
            print('This server is enabled already...')
            return 'This server is enabled already'
        if ip_address != server['host']:
            print('Incorrect ip address, please check it...')
            return 'Incorrect ip address'
        else:
            try:
                result = c.slb.server.update(server_name, ip_address)
                server = result['server']
                if server['action'] == 'enable':
                    print("Success to enable the server of: " + server_name)
                    return 'Success enable server'
                else:
                    print("Failed to enable the server of " + server_name + ', please try again')
            except Exception as e:
                print("Cannot enable the server of: " + server_name + ". The error message is: " + str(e))

    def enable_all_servers(self, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        try:
            json_string = c.slb.service_group.all()
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
                        server_json = c.slb.server.get(server['name'])
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
                            self.enable_server(server['name'], server['host'])
                        except Exception as e:
                            print(str(e))
                            continue

    def disable_server(self, server_name, ip_address, admin, password):
        try:
            c = self.get_acos_lient(admin, password)
        except Exception as e:
            print("Cannot establish the connection. The error message is: " + str(e))
            return
        try:
            json_string = c.slb.server.get(server_name)
        except Exception as e:
            print("Cannot get the information of the server " + server_name + ". The error message is: " + str(e))
            return 'Cannot get the information of the server'

        server = json_string['server']
        if server['action'] == 'disable':
            print('This server is disabled already...')
            return 'This server is disabled already'
        if ip_address != server['host']:
            print('Incorrect ip address, please check it...')
            return 'Incorrect ip address'
        else:
            try:
                result = c.slb.server.update(server_name, ip_address, status=0)
                server = result['server']
                if server['action'] == 'disable':
                    print("Success to disable the server of: " + server_name)
                    return 'Success disable server'
                else:
                    print("Failed to disable the server of " + server_name + ', please try again')

            except Exception as e:
                print("Cannot disable the server of: " + server_name + ". The error message is: " + str(e))

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-lg", '--groupName', help="List all service group or one group")
        parser.add_argument("-ls", '--status', help="List servers according to state")
        parser.add_argument("-ss", '--serverName', help="Show a server's information")
        parser.add_argument("-es", "--disabledServerName", "--disabledServerIP", help="Enable a server")
        parser.add_argument("-ds", "--enabledServerName", "--enabledServerIP", help="Disable a server")
        parser.add_argument("-ip", "--ipAddress", help="Ip address of server")
        parser.add_argument("-ad", "--adminName", help="Admin name")
        parser.add_argument("-pw", "--password", help="Admin password")

        args = parser.parse_args()
        if args.adminName and args.password:
            if args.groupName:
                self.list_service_group(args.groupName, args.adminName, args.password)
            if args.status:
                self.list_servers(args.status, args.adminName, args.password)
            if args.serverName:
                self.show_server_info(args.serverName, args.adminName, args.password)
            if args.disabledServerName and args.ipAddress:
                self.enable_server(args.disabledServerName, args.ipAddress, args.adminName, args.password)
            if args.enabledServerName and args.ipAddress:
                self.disable_server(args.enabledServerName, args.ipAddress, args.adminName, args.password)
            if args.disabledServerName == 'all':
                self.enable_all_servers(args.adminName, args.password)


if __name__ == '__main__':
    lb = LoadBalancer()
    lb.main()
