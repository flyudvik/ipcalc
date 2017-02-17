from flask import Flask, json, render_template, request
from flask import flash
from werkzeug.contrib.cache import SimpleCache

import exceptions
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
    sizes = json.loads(sizes_str)
    try:
        get_hash = hash(network + sizes_str)
        context = cache.get(get_hash)
        if not context:
            context = utils.ip_calculator(network, sizes)
            cache.set(get_hash, context, timeout=5 * 60)
        return render_template('result.html', context=context)
    except Exception as e:
        flash(str(e), 'error')
        return render_template("index.html", context={
            'network': network,
            'sizes': sizes
        })


@exceptions.deprecated
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


app.secret_key = 'kjsdhflkjshflskjdfhlksdfhbvlksefvouhoue,flaedkfhdskf'
if __name__ == '__main__':
    app.run()
