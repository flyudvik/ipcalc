from flask import Flask, json, render_template, request
from flask import flash
from werkzeug.contrib.cache import SimpleCache

import utils


app = Flask(__name__)
CACHE_TIMEOUT = 2 * 60 * 60


cache = SimpleCache()


class cached(object):
    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.full_path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.full_path, response, self.timeout)
            return response
        return decorator


@app.route('/', methods=['GET'])
@cached()
def ipcalc():
    network = request.args.get('network')
    sizes_str = request.args.get('size')
    if not network or not sizes_str:
        return render_template("index.html")
    sizes = json.loads(sizes_str)
    try:
        context = utils.ip_calculator(network, sizes)
        return render_template('result.html', context=context)
    except Exception as e:
        flash(str(e), 'error')
        return render_template("index.html", context={
            'network': network,
            'sizes': sizes
        })


@app.template_filter('to_bit')
def to_bit_filter(address, version=4):
    if version == 4:
        br = bin(int(address))[2:].zfill(32)
        br = br[:8] + '.' + br[8:16] + '.' + br[16:24] + '.' + br[24:]
        return br
    elif version == 6:
        return "IPv6 not supported yet"
    else:
        return f"Version {version} is not supported."


app.secret_key = 'kjsdhflkjshflskjdfhlksdfhbvlksefvouhoue,flaedkfhdskf'
if __name__ == '__main__':
    app.run()
