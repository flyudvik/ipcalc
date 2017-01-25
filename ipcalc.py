from flask import Flask
from flask import json
from flask import render_template
from flask import request
from werkzeug.contrib.cache import SimpleCache

import utils

app = Flask(__name__)


cache = SimpleCache()


@app.route('/', methods=['GET'])
def hello_world():
    network = request.args.get('network', '192.168.0.0/24')
    sizes_str = request.args.get('size', '[]')
    get_hash = hash(network + sizes_str)
    context = cache.get(get_hash)
    if not context:
        context = {
            'empty': True,
        }
    if context['empty']:
        sizes = json.loads(sizes_str)
        context['network'] = utils.string_2_network(network)
        context['sizes'] = sizes
        print(len(sizes))
        if network and len(sizes):
            required_hosts = utils.get_hosts_with_interface(sizes)
            subnets = utils.get_subnets_plain(utils.string_2_network(network), min=min(required_hosts))
            context['initial_table'] = utils.display_horizontal_table_div(subnets)
            hosts, news_subnets = utils.extract_for_hosts(required_hosts, subnets)
            context['reduced_table'] = utils.display_horizontal_table_div(news_subnets)
            context['hosts'] = hosts
            context['required_num_addresses'] = sum(sizes)
            context['empty'] = False
            cache.set(get_hash, context, timeout=5*60)
    return render_template("index.html", context=context)



if __name__ == '__main__':
    app.run()
