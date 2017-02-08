from flask import Flask, json, render_template, request
from werkzeug.contrib.cache import SimpleCache


import utils
from exceptions import *


app = Flask(__name__)


cache = SimpleCache()


@app.route('/', methods=['GET'])
def ipcalc():
    network = request.args.get('network')
    sizes_str = request.args.get('size')
    if not network or not sizes_str:
        return render_template("index.html")
    get_hash = hash(network + sizes_str)
    context = cache.get(get_hash)
    if not context:
        context = {}
        sizes = json.loads(sizes_str)
        context['network'] = utils.string_2_network(network)
        context['sizes'] = sizes
        subnets = utils.extract_for_network(utils.string_2_network(network), sizes)
        context['networks'] = zip(reversed(sorted(sizes)), subnets)
        context['dedicated'] = sum(map(lambda x: x.num_addresses, subnets))
        cache.set(get_hash, context, timeout=5 * 60)
    return render_template('result_2.html', context=context)


@app.route('/deprecated', methods=['GET'])
def hello_world():
    network = request.args.get('network')
    sizes_str = request.args.get('size')
    if not network or not sizes_str:
        return render_template("index.html")
    try:
        get_hash = hash(network + sizes_str)
        context = cache.get(get_hash)
        if not context:
            context = {}
            sizes = json.loads(sizes_str)
            context['network'] = utils.string_2_network(network)
            context['sizes'] = sizes
            required_hosts = utils.get_hosts_with_interface(sizes)
            subnets = utils.get_subnets_plain(
                utils.string_2_network(network), min=min(required_hosts)
            )
            networks, new_subnets = utils.extract_for_hosts(
                required_hosts, subnets
            )
            context['networks'] = networks
            context['dedicated'] = utils.count_dedicated_ip(networks)
            cache.set(get_hash, context, timeout=5 * 60)
        return render_template("result.html", context=context)
    except IPCalcBaseException as e:
        return render_template("error.html", exception=e)


if __name__ == '__main__':
    app.run()
