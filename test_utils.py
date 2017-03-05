import unittest
from pprint import pprint

from flask import json

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

    def test_success_for_single_network(self):
        network = ipaddress.ip_network('192.168.0.0/24')
        required_hosts = [250]
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


class TestParseSizesStr(unittest.TestCase):
    def test_json_input(self):
        payload = [123, 34, 56, 78]
        json_payload = json.dumps(payload)
        self.assertEqual(
            payload,
            utils.parse_sizes_str(json_payload)
        )

    def test_space_separated_input(self):
        payload = [123, 34, 56, 78]
        space_payload = ' '.join(map(str, payload))
        self.assertEqual(payload, utils.parse_sizes_str(space_payload))

    def test_comma_separated_input(self):
        payload = [123, 34, 56, 78]
        space_payload = ','.join(map(str, payload))
        self.assertEqual(payload, utils.parse_sizes_str(space_payload))

    def test_really_idiotic_way_to_separate_input(self):
        payload = [123, 34, 56, 78]
        idiot_payload = '123, 34 56;78'
        self.assertEqual(payload, utils.parse_sizes_str(idiot_payload))

    def test_single_input(self):
        payload = [123]
        payload_as_str = '123'
        self.assertEqual(payload, utils.parse_sizes_str(payload_as_str))

    def test_single_with_comma_input(self):
        payload = [123]
        payload_as_str = '123,'
        self.assertEqual(payload, utils.parse_sizes_str(payload_as_str))

    def test_single_with_space_input(self):
        payload = [123]
        payload_as_str = '123 '
        self.assertEqual(payload, utils.parse_sizes_str(payload_as_str))

    def test_single_json_input(self):
        payload = [123]
        payload_as_str = '[123]'
        self.assertEqual(payload, utils.parse_sizes_str(payload_as_str))

    def test_null_input(self):
        self.assertEqual([], utils.parse_sizes_str(''))

    def test_null_json_input(self):
        self.assertEqual([], utils.parse_sizes_str('[]'))

    def test_null_separator_input(self):
        self.assertEqual([], utils.parse_sizes_str(',;;;,, ;, ;, ;,; ;'))

    def test_multiple_consequence_separators(self):
        payload = [123, 34, 45]
        payload_as_str = '123,,,;34; 45; '
        self.assertEqual(payload, utils.parse_sizes_str(payload_as_str))
