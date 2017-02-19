from flask import Flask, json, render_template, request
from flask import flash
from werkzeug.contrib.cache import SimpleCache

import utils


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


app.secret_key = 'kjsdhflkjshflskjdfhlksdfhbvlksefvouhoue,flaedkfhdskf'
if __name__ == '__main__':
    app.run()
