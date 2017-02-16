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
            context = {}
            context['network'] = utils.string_2_network(network)
            context['sizes'] = sizes
            subnets = utils.extract_for_network(utils.string_2_network(network), sizes)
            context['networks'] = zip(reversed(sorted(sizes)), subnets)
            context['dedicated'] = sum(map(lambda x: x.num_addresses, subnets))
            context['chart'] = json.dumps(
                utils.create_graph_of_network_relations(
                    subnets, context['network']
                )
            )
            cache.set(get_hash, context, timeout=5 * 60)
        return render_template('result.html', context=context)
    except Exception as e:
        flash(str(e), 'error')
        return render_template("index.html", context={
            'network': network,
            'sizes': sizes
        })


app.secret_key = 'kjsdhflkjshflskjdfhlksdfhbvlksefvouhoue,flaedkfhdskf'
if __name__ == '__main__':
    app.run()
