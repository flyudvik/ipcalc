import ipaddress

from exceptions import *


def string_2_network(string: str):
    return ipaddress.ip_network(string)


def close_to_power_two(x):
    return 1 << (x - 1).bit_length()


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
