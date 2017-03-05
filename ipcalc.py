import collections
from flask import Flask, json, render_template, request
from flask import flash, session
from flask_cache import Cache
from datetime import datetime
import humanize

import utils


app = Flask(__name__)
CACHE_TIMEOUT = 2 * 60 * 60


cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/', methods=['GET'])
def ipcalc():
    network = request.args.get('network')
    sizes_str = request.args.get('size')
    latest = collections.deque(session.get('latest', []), maxlen=5)
    sizes = utils.parse_sizes_str(sizes_str) if sizes_str else []
    if not network or not sizes:
        flash('Enter your network and list of networks', 'info')
        return render_template("index.html", latest=latest)
    if not latest:
        latest = collections.deque(maxlen=5)
    latest.append({
        'time': datetime.now(),
        'path': request.full_path,
        'network': network,
        'sizes': sizes
    })
    session['latest'] = list(latest)
    try:
        if len(sizes) >= 20:
            sizes = sizes[:20]
            raise Exception("Your browser probably cannot handle this")
        context = get_context(network, sizes)
        return render_template('index.html', context=context, latest=latest, calculated=True)
    except Exception as e:
        flash(str(e), 'error')
        return render_template("index.html", context={
            'network': network,
            'sizes': sizes
        }, latest=latest)


@cache.memoize(timeout=600)
def get_context(network, sizes):
    return utils.ip_calculator(network, sizes)


@app.route('/about/', methods=['GET'])
@cache.cached(timeout=999999)
def discus():
    return render_template('discus.html')


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


@app.template_filter()
def natural_time(dt):
    return humanize.naturaltime(datetime.now() - dt)


app.secret_key = 'kjsdhflkjshflskjdfhlksdfhbvlksefvouhoue,flaedkfhdskf'
if __name__ == '__main__':
    app.run()
