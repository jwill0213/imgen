from flask import Flask, render_template, request, g, jsonify, make_response


app = Flask(__name__)

@app.before_first_request
def init_app():
    from utils.endpoint import endpoints as endpnts
    global endpoints
    endpoints = endpnts
    import endpoints as _  # noqa: F401

@app.route('/')
def index():
    return render_template('index.html', active_home="nav-active")


@app.route('/endpoints.json', methods=['GET'])
def endpoints():
    return jsonify({"endpoints": [{'name': x, 'parameters': y.params, 'ratelimit': f'{y.rate}/{y.per}s'} for x, y in endpoints.items()]})


@app.route('/api/<endpoint>', methods=['GET', 'POST'])
def api(endpoint):
    if endpoint not in endpoints:
        return jsonify({'status': 404, 'error': 'Endpoint {} not found!'.format(endpoint)}), 404
    if request.method == 'GET':
        text = request.args.get('text', '')
        avatars = [x for x in [request.args.get('avatar1', request.args.get('image', None)),
                               request.args.get('avatar2', None)] if x]
        usernames = [x for x in [request.args.get('username1', None), request.args.get('username2', None)] if x]
        kwargs = {}
        for arg in request.args:
            if arg not in ['text', 'username1', 'username2', 'avatar1', 'avatar2']:
                kwargs[arg] = request.args.get(arg)
    else:
        if not request.is_json:
            return jsonify({'status': 400, 'message': 'when submitting a POST request you must provide data in the '
                                                      'JSON format'}), 400
        request_data = request.json
        text = request_data.get('text', '')
        avatars = list(request_data.get('avatars', list(request_data.get('images', []))))
        usernames = list(request_data.get('usernames', []))
        kwargs = {}
        for arg in request_data:
            if arg not in ['text', 'avatars', 'usernames']:
                kwargs[arg] = request_data.get(arg)
    try:
        result = endpoints[endpoint].run(key='', text=text,
                                         avatars=avatars,
                                         usernames=usernames,
                                         kwargs=kwargs)
    except IndexError as e:
        return jsonify({'status': 400, 'error': str(e) + '. Are you missing a parameter?'}), 400
    except Exception as e:
        return jsonify({'status': 500, 'error': str(e)}), 500

    return result, 200


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
