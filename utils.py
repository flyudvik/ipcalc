import ipaddress

from flask import json

from exceptions import *


def string_2_network(string: str):
    return ipaddress.ip_network(string)


@deprecated
def get_subnets_plain(network, **kwargs):
    if network.num_addresses == 1:
        raise WrongNetworkException('One available address')
    if network.num_addresses <= kwargs.get('min', 4):
        raise WrongNetworkException('Expect to have bigger network or make minimum reqired hosts less')
    res = {}
    stack = [network]
    while len(stack):
        current_network = stack.pop()
        power = current_network.num_addresses
        if power > kwargs.get('min', 4) + 2:
            for subnet in current_network.subnets():
                stack.append(subnet)
        res[power] = res.get(power, []) + [current_network]
    return res


def close_to_power_two(x):
    return 1 << (x - 1).bit_length()


def reduce_subnets(new_subnets):
    res = {}
    for power, subnet in new_subnets.items():
        if len(subnet):
            res[power] = subnet
    return res


@deprecated
def extract_for_hosts(hosts: list, subnets: dict) -> (list, dict):
    if not hosts:
        raise WrongNumberOfHosts("Hosts list should contain "
                         "at least 1 required network of hosts")
    if not subnets:
        raise WrongNetworkException("Subnets should be at least contain one network key")
    if sum(map(close_to_power_two, hosts)) > max(subnets.keys()):
        raise WrongNumberOfHosts("sum of the required hosts "
                         "should be less than "
                         "maximal possible number"
                         " of host for this network")
    new_subnets = subnets.copy()
    result = []
    for host in reversed(sorted(hosts)):
        power = close_to_power_two(host+2)
        parent_to_remove = new_subnets[power].pop()
        result.append((host, parent_to_remove))
        stack = list(parent_to_remove.subnets())
        while len(stack):
            current_subnet = stack.pop()
            power = current_subnet.num_addresses
            if power >= min(subnets.keys()):
                for subnet in current_subnet.subnets():
                    stack.append(subnet)
                if current_subnet in new_subnets[power]:
                    new_subnets[power].remove(current_subnet)
    new_subnets = reduce_subnets(new_subnets)
    return result, new_subnets


def get_max_summary_height(data):
    max_key_sum = 0
    prev = 0
    print(sorted(map(lambda x: len(x), data.values()), reverse=True))
    for i, value in enumerate(sorted(map(lambda x: len(x), data.values()), reverse=True)):
        if value * 2 > prev:
            key_sum = 2**i * value
            if key_sum > max_key_sum:
                max_key_sum = key_sum
        prev = value
    print(f"max_key_sum = {max_key_sum}")
    return max_key_sum


@deprecated
def display_horizontal_table_div(data):
    body = """<div class="_table">"""
    height = max(data.keys()) // min(data.keys())
    max_summary = get_max_summary_height(data)
    max_height = max_summary
    for value_list in data.values():
        sum_height = 0
        col = '<div class="_col">'
        for value in value_list:
            if sum_height < max_summary:
                cur_height = height if height < max_height else max_height
            else:
                cur_height = max_summary - sum_height
            cell = '<div class="_cell" style="height:{}em">{}</div>\n'.format(
                cur_height,
                value)
            col += cell
            sum_height += height
        col += '</div>\n'
        body += col
        height >>= 1
    body += '</div>'
    return body


def get_hosts_with_interface(sizes):
    return sizes


def count_dedicated_ip(networks):
    return sum(map(lambda x: x[1].num_addresses, networks))


def extract_for_network(network, required_hosts: list) -> list:
    if not required_hosts:
        raise WrongNumberOfHosts("Hosts list should contain "
                         "at least 1 required network of hosts")
    if not network.num_addresses:
        raise WrongNetworkException("Subnets should be at least contain one network key")
    if sum(map(close_to_power_two, required_hosts)) > network.num_addresses:
        raise WrongNumberOfHosts("sum of the required hosts "
                         "should be less than "
                         "maximal possible number"
                         " of host for this network")
    required_hosts = sorted(map(lambda x: x+2, required_hosts))

    stack = list(network.subnets())
    stack.reverse()

    result = []
    item_to_pull = required_hosts.pop()
    while stack:
        subnet = stack.pop()
        if subnet.num_addresses == close_to_power_two(item_to_pull):
            result.append(subnet)
            try:
                item_to_pull = required_hosts.pop()
            except IndexError:
                break
        elif subnet.num_addresses > close_to_power_two(item_to_pull):
            stack.extend(list(reversed(list(subnet.subnets()))))
    return result


def create_matrix_network_graph(subnets):
    matrix = [[0 for _ in subnets] for _ in subnets]
    r = sorted(subnets)

    for i, network in enumerate(r):
        for j, subnet_2 in enumerate(r):
            if subnet_2 in network.subnets():
                matrix[i][j] = 1

    return matrix


def _check_network(network, set_of_networks):
    for n in set_of_networks:
        if n == network:
            return True
    if network > max(set_of_networks):
        return True
    return False


def _network_has_nodes(network, set_of_networks):
    for n in set_of_networks:
        if n == network:
            return False
    return True


def create_graph_of_network_relations(result, network):
    if _check_network(network, result):
        if _network_has_nodes(network, result):
            return None
        return {
            'text': {
                'name': network.compressed
            }
        }
    subnets = []
    for subnet in network.subnets():
        s = create_graph_of_network_relations(result, subnet)
        if s is not None:
            subnets.append(s)
    return {
        'text': {
            "name": network.compressed,
        },
        'children': subnets,
    }


def ip_calculator(network, sizes):
    network = string_2_network(network)
    subnets = extract_for_network(string_2_network(network), sizes)
    networks = zip(reversed(sorted(sizes)), subnets)
    return {
        'network': network,
        'sizes': sizes,
        'networks': networks,
        'dedicated': sum(map(lambda x: x.num_addresses, subnets)),
        'chart': json.dumps(create_graph_of_network_relations(subnets, network))
    }
