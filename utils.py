import ipaddress

from exceptions import *


def string_2_network(string: str):
    return ipaddress.ip_network(string)


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
