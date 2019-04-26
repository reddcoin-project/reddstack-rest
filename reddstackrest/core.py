import json
from twisted.internet.defer import inlineCallbacks, returnValue
from klein import Klein
from blockstore_client import config, client

app = Klein()

conf = config.get_config()
conf["network"] = "mainnet"
proxy = client.session(conf, conf['server'], conf['port'])


with app.subroute("/") as app:
    @app.route('/')
    def pg_root(request):
        request.setHeader('Content-Type', 'application/json')
        responsebody = {'msg': 'this is root'}
        return json.dumps(responsebody)


    @app.route('/about')
    def pg_about(request):
        request.setHeader('Content-Type', 'application/json')
        responsebody = {'msg': 'this is about'}
        return json.dumps(responsebody)


    with app.subroute('/api'):

        with app.subroute('/v1'):

            # Returns server status
            # http://<url>/api/<version>/status
            @app.route('/status')
            @inlineCallbacks
            def pg_api_status(request):
                request.setHeader('Content-Type', 'application/json')
                responsebody = yield client.getinfo()

                if 'traceback' in responsebody:
                    del responsebody['traceback']

                returnValue(json.dumps(responsebody))

            # Returns consensus with optional height
            # http://<url>/api/<version>/consensus
            # http://<url>/api/<version>/consensus?height=<height>
            @app.route('/consensus')
            @inlineCallbacks
            def pg_api_consensus(request):
                request.setHeader('Content-Type', 'application/json')
                responsebody = {}

                if 'height' in request.args:
                    height = int(request.args['height'][0])
                else:
                    height = yield client.getinfo()['last_block']

                responsebody['height'] = height

                responsebody['consensus'] = yield client.get_consensus_at(height)

                if 'traceback' in responsebody:
                    del responsebody['traceback']

                returnValue(json.dumps(responsebody))

            # Returns all names in all blockspaces with optional offset and count
            # http[s]://<url>/api/<version>/names
            # http[s]://<url>/api/<version>/names?count=<count>&offset=<offset>
            # eg http[s]://localhost/api/v1/names?count=100&offset=0
            @app.route('/names')
            @inlineCallbacks
            def pg_api_names(request):
                request.setHeader('Content-Type', 'application/json')
                responsebody = {}
                count = None
                offset = None
                if 'count' in request.args:
                    count = int(request.args['count'][0])
                    responsebody['count'] = count
                if 'offset' in request.args:
                    offset = int(request.args['offset'][0])
                    responsebody['offset'] = offset

                responsebody['names'] = yield client.get_all_names(offset, count)

                if 'traceback' in responsebody:
                    del responsebody['traceback']

                returnValue(json.dumps(responsebody))

            # Sub-route ./name
            with app.subroute('/name'):

                # Returns cost of user id
                # http[s]://<url>/api/<version>/name/cost?userid=<user.id>
                # e.g http[s]://<url>/api/<version>/name/cost?userid=example.user
                @app.route('/cost')
                @inlineCallbacks
                def pg_api_name_cost(request):
                    request.setHeader('Content-Type', 'application/json')
                    responsebody = {}

                    if 'userid' in request.args:
                        userid = str(request.args['userid'][0])
                        # Check if user exists
                        response = yield client.get_name_blockchain_record(str(userid))

                        print response
                        responsebody['uid'] = userid

                        if 'error' in response:
                            if response['error'] == 'Not found.':  # user does not exist, retrieve cost
                                responsebody['status'] = 'not found'

                                responsebody['cost'] = yield client.get_name_cost(str(userid))
                        elif response['name'] is not None:
                                responsebody['status'] = 'found'
                        elif 'traceback' in response:
                            del response['traceback']
                            returnValue(json.dumps(response))

                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    returnValue(json.dumps(responsebody))

                # Returns transaction details for a user id preorder
                # http[s]://<url>/api/<version>/name/preorder?userid=<user.id>
                # e.g http[s]://<url>/api/<version>/name/preorder?userid=example.user
                # Returns json containing unsigned transaction and the inputs needed to create the transaction
                @app.route('/preorder')
                @inlineCallbacks
                def pg_api_name_preorder(request):
                    request.setHeader('Content-Type', 'application/json')
                    userid = None
                    publickey = None
                    owningaddr = None
                    responsebody = {}
                    if 'userid' in request.args and 'owningaddr' in request.args and 'publickey' in request.args:
                        userid = str(request.args['userid'][0])
                        owningaddr = str(request.args['owningaddr'][0])
                        publickey = str(request.args['publickey'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    responsebody = yield client.preorder_unsigned(userid, publickey, owningaddr)

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns transaction details for a user id registration
                # http[s]://<url>/api/<version>/name/register?userid=<user.id>
                # e.g http[s]://<url>/api/<version>/name/register?userid=example.user
                # Returns json containing unsigned transaction and the inputs needed to create the transaction
                @app.route('/register')
                @inlineCallbacks
                def pg_api_name_register(request):
                    request.setHeader('Content-Type', 'application/json')
                    userid = None
                    publickey = None
                    owningaddr = None
                    responsebody = {}
                    if 'userid' in request.args and 'owningaddr' in request.args and 'publickey' in request.args:
                        userid = str(request.args['userid'][0])
                        owningaddr = str(request.args['owningaddr'][0])
                        publickey = str(request.args['publickey'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    responsebody = yield client.register_unsigned(userid, publickey, owningaddr)

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns transaction details for a user id update
                # http[s]://<url>/api/<version>/name/update?userid=<user.id>&profile=<profile>&publickey=<publickey>&tx_hash=<tx_hash>
                # e.g http[s]://<url>/api/<version>/name/update?userid=example.user
                # Returns json containing unsigned transaction and the inputs needed to create the transaction
                @app.route('/update', methods=['POST'])
                @inlineCallbacks
                def pg_api_name_update(request):
                    request.setHeader('Content-Type', 'application/json')
                    payload = request.content.read()
                    userid = None
                    publickey = None
                    tx_hash = None
                    responsebody = {}
                    if 'userid' in request.args and 'publickey' in request.args:
                        userid = str(request.args['userid'][0])
                        publickey = str(request.args['publickey'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    if 'tx_hash' in request.args:
                        tx_hash = str(request.args['tx_hash'][0])

                    if tx_hash is not None:
                        # if we have tx_hash, need the complete profile transaction
                        responsebody = yield client.update(userid, payload, publickey, tx_hash)
                    else:
                        # generate the update profile transaction
                        responsebody = yield client.update_unsigned(userid, payload, publickey)

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns details for a user id
                # http[s]://<url>/api/<version>/name/lookup?userid=<user.id>
                # e.g http[s]://<url>/api/<version>/name/lookup?userid=example.user
                # Returns json containing profile details
                @app.route('/lookup')
                @inlineCallbacks
                def pg_api_name_lookup(request):
                    request.setHeader('Content-Type', 'application/json')
                    userid = None
                    responsebody = {}
                    if 'userid' in request.args:
                        userid = str(request.args['userid'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    responsebody = yield client.get_name_blockchain_record(userid)

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns profile details for a user id
                # http[s]://<url>/api/<version>/name/profile?userid=<user.id>
                # e.g http[s]://<url>/api/<version>/name/profile?userid=example.user
                # Returns json containing profile details
                @app.route('/profile')
                @inlineCallbacks
                def pg_api_name_profile(request):
                    request.setHeader('Content-Type', 'application/json')
                    userid = None
                    hash = None
                    responsebody = {}
                    if 'userid' in request.args and 'hash' in request.args:
                        userid = str(request.args['userid'][0])
                        hash = str(request.args['hash'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    response = yield client.get_immutable(userid, hash)

                    if 'data' in response:
                        responsebody['data'] = json.loads(response['data'])
                    else:
                        responsebody = response

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns names owned by address
                # http[s]://<url>/api/<version>/name/ownedby?address=<reddcoin address>
                # e.g http[s]://<url>/api/<version>/name/ownedby?address=
                # Returns json containing profile details
                @app.route('/ownedby')
                @inlineCallbacks
                def pg_api_name_ownedby(request):
                    request.setHeader('Content-Type', 'application/json')
                    address = None
                    responsebody = {}
                    if 'address' in request.args:
                        address = str(request.args['address'][0])
                    else:
                        responsebody['error'] = 'Missing parameters'
                        returnValue(json.dumps(responsebody))

                    responsebody = yield client.get_names_owned_by_address(address)

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

            # Returns details of user id
            # http[s]://<url>/api/<version>/name?userid=<user.id>
            # e.g http[s]://<url>/api/<version>/name?userid=example.user
            @app.route('/name')
            @inlineCallbacks
            def pg_api_name(request):
                request.setHeader('Content-Type', 'application/json')
                responsebody = {}
                if 'userid' in request.args:
                    username = str(request.args['userid'][0])
                    responsebody['blockchain_record'] = yield client.get_name_blockchain_record(str(username))

                    if 'block_number' in responsebody['blockchain_record'] and responsebody['blockchain_record']['value_hash'] is not None:
                        data_id = responsebody['blockchain_record']['value_hash']
                        response = yield client.get_immutable(str(username), data_id)
                        if 'error' in response:
                            responsebody['data_record'] = response['error']
                        else:
                            responsebody['data_record'] = json.loads(response['data'])

                else:
                    responsebody['error'] = 'No userid provided'

                if 'traceback' in responsebody:
                    del responsebody['traceback']

                returnValue(json.dumps(responsebody))

            # Sub-route ./namespace
            with app.subroute('/namespace'):

                # Returns all names in all blockspaces with optional offset and count
                # http[s]://<url>/api/<version>/namespace/names
                # http[s]://<url>/api/<version>/namespace/names?namespace=<namespace>&count=<count>&offset=<offset>
                # eg http[s]://localhost/api/v1/namespace/names?namespace=tester&count=100&offset=0
                @app.route('/names')
                @inlineCallbacks
                def pg_api_namespace_names(request):
                    request.setHeader('Content-Type', 'application/json')
                    responsebody = {}
                    count = None
                    offset = None
                    ns = None
                    if 'namespace' in request.args:
                        ns = str(request.args['namespace'][0])
                    if 'count' in request.args:
                        count = int(request.args['count'][0])
                        responsebody['count'] = count
                    if 'offset' in request.args:
                        offset = int(request.args['offset'][0])
                        responsebody['offset'] = offset

                    if ns is not None:
                        response = yield client.get_names_in_namespace(ns, offset, count)
                        if 'error' not in response:
                            responsebody['results'] = response['results']
                    else:
                        responsebody['error'] = 'No namespace provided'

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

                # Returns all cost of creating a namespace
                # http[s]://<url>/api/<version>/namespace/cost?namespace=<namespaceid>
                # eg http[s]://localhost/api/v1/namespace/cost?namespace=tester
                @app.route('/cost')
                @inlineCallbacks
                def pg_api_namespace_cost(request):
                    request.setHeader('Content-Type', 'application/json')
                    responsebody = {}
                    ns = None
                    if 'namespace' in request.args:
                        ns = str(request.args['namespace'][0])
                    if ns is not None:
                        responsebody = yield client.get_namespace_cost(str(ns))
                    else:
                        responsebody['error'] = 'No namespace provided'

                    if 'traceback' in responsebody:
                        del responsebody['traceback']

                    returnValue(json.dumps(responsebody))

            # Returns details about a blockspace
            # http[s]://<url>/api/<version>/namespace?namespace=<namespaceid>
            # eg http[s]://localhost/api/v1/namespace?namespace=tester
            @app.route('/namespace')
            @inlineCallbacks
            def pg_api_namespace(request):
                request.setHeader('Content-Type', 'application/json')
                responsebody = {}
                ns = None
                if 'namespace' in request.args:
                    ns = str(request.args['namespace'][0])
                if ns is not None:
                    responsebody = yield client.get_namespace_blockchain_record(str(ns))
                else:
                    responsebody['error'] = 'No namespace provided'

                if 'traceback' in responsebody:
                    del responsebody['traceback']

                returnValue(json.dumps(responsebody))

resource = app.resource
