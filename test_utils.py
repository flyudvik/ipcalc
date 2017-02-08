import unittest
import ipaddress
import utils


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


class TestExtractForHosts(unittest.TestCase):
    def setUp(self):
        self.network = ipaddress.ip_network('1.1.0.0/24')
        self.hosts = [127, 32, 32]
        self.subnets = utils.get_subnets_plain(self.network)

    def test_fail_zero_number_of_hosts(self):
        with self.assertRaises(ValueError):
            utils.extract_for_hosts(hosts=[], subnets=self.subnets)

    def test_fail_too_much_required(self):
        with self.assertRaises(ValueError):
            utils.extract_for_hosts(hosts=[64, 64, 32, 12], subnets={128: []})

    def test_fail_empty_subnets(self):
        with self.assertRaises(ValueError):
            utils.extract_for_hosts(self.hosts, subnets={})

    def test_success(self):
        hosts, subnets = utils.extract_for_hosts(self.hosts, self.subnets)
        self.assertEqual(3, len(hosts))
        self.assertEqual(len(subnets[128]), 1)


class TestGetSubnetsPlain(unittest.TestCase):
    def setUp(self):
        self.network = ipaddress.ip_network('1.1.1.0/24')

    def test_success(self):
        sn = utils.get_subnets_plain(self.network)
        self.assertEqual(7, len(sn.keys()))
        self.assertIn(4, sn.keys())
        self.assertIn(256, sn.keys())

        self.assertEqual([self.network], sn[256])
        self.assertEqual(64, len(sn[4]))

    def test_success_2(self):
        sn = utils.get_subnets_plain(self.network, min=32)
        self.assertNotIn(4, sn.keys())
        self.assertIn(256, sn.keys())
        self.assertIn(32, sn.keys())
        self.assertNotIn(16, sn.keys())

        self.assertEqual([self.network], sn[256])
        self.assertEqual(8, len(sn[32]))

    def test_fail_empty_network(self):
        with self.assertRaises(ValueError):
            utils.get_subnets_plain(ipaddress.ip_network('255.255.255.255/32'))

    def test_fail_zero_subnets(self):
        with self.assertRaises(ValueError):
            sn = utils.get_subnets_plain(ipaddress.ip_network('255.255.255.0/25'), min=256)

    def test_fail_wrong_type(self):
        with self.assertRaises(AttributeError):
            utils.get_subnets_plain({})
        with self.assertRaises(AttributeError):
            utils.get_subnets_plain('')
        with self.assertRaises(AttributeError):
            utils.get_subnets_plain([])


class TestExtractForNetwork(unittest.TestCase):
    def test_success(self):
        network = ipaddress.IPv4Network('192.168.0.0/24')
        required_hosts = [126, 2, 2, 2, 2, 30, 28]
        result = utils.extract_for_network(network, required_hosts)
        self.assertEqual(len(result), len(required_hosts))
