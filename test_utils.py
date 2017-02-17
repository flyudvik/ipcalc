import unittest
from pprint import pprint

import utils
from utils import ipaddress


class TestUtils(unittest.TestCase):
    def test_string_2_network(self):
        string = '1.1.1.0/24'
        self.assertEqual(
            utils.string_2_network(string),
            ipaddress.ip_network(string)
        )

    def test_close_to_power_two(self):
        self.assertEqual(256,
                         utils.close_to_power_two(255))
        self.assertEqual(256,
                         utils.close_to_power_two(129))
        self.assertEqual(256,
                         utils.close_to_power_two(256))
        self.assertLess(256,
                         utils.close_to_power_two(257))


class TestExtractForNetwork(unittest.TestCase):
    def test_success(self):
        network = ipaddress.IPv4Network('192.168.0.0/24')
        required_hosts = [126, 2, 2, 2, 2, 30, 28]
        result = utils.extract_for_network(network, required_hosts)
        self.assertEqual(len(result), len(required_hosts))

    def test_create_graph_of_network_relations(self):
        top_network = ipaddress.ip_network("192.168.0.0/24")
        required_hosts = [125, 36, 30]
        result = utils.extract_for_network(top_network, required_hosts)
        self.assertEqual(len(result), len(required_hosts))

        graph = utils.create_graph_of_network_relations(result, top_network)

        network_for_125 = list(top_network.subnets())[0]

        self.assertEqual(type(graph), dict)
        self.assertEqual(graph['text']['name'], top_network.compressed)
        self.assertEqual(graph['children'][0]['text']['name'], network_for_125.compressed)
