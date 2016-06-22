import os
import yaml
import bottle
from bottle_swagger import SwaggerPlugin

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

bottle.install(EnableCors())

# Set up swagger
this_dir = os.path.dirname(os.path.abspath(__file__))
with open("{0}/swagger.yml".format(this_dir)) as f:
    swagger_def = yaml.load(f)

bottle.install(SwaggerPlugin(swagger_def,
                             ignore_undefined_routes=True,
                             validate_requests=False,
                             validate_responses=False))

# Just store events and actions in memory for demo
events = []
EVENT_FIELDS = ('type', 'source', 'name', 'value', 'current')

actions = []
ACTION_FIELDS = ('type', 'target', 'name', 'value', 'processed')

config = {
    'sources': [],
    'targets': []
}

@bottle.route('/')
def index():
    return bottle.static_file('index.html', root=this_dir)

@bottle.route('/docs')
def docs_index():
    bottle.redirect("/docs/index.html")

@bottle.route('/docs/<filename:path>')
def docs(filename):
    return bottle.static_file(filename, root=this_dir + "/swagger-ui")

@bottle.route('/config', method='GET')
def show_config():
    return config

@bottle.route('/config', method='POST')
def set_config():
    config = sanitize_config(bottle.request.json)

    return config

@bottle.route('/events', method='GET')
def list_events():
    found_events = events
    current_events = [ event for event in events if event.get('current', True) ]
    for event in current_events:
        event['current'] = False

    return dict(events=events[-1:-6:-1])

@bottle.route('/events', method='POST')
def add_event():
    event = sanitize_event(bottle.request.json)
    event['current'] = True

    events.append(event)

    return event

@bottle.route('/actions', method='GET')
def list_actions():
    current_actions = [ action for action in actions if not action.get('processed', False) ]
    for action in current_actions:
        action['processed'] = True

    return dict(actions=current_actions)

@bottle.route('/actions', method='POST')
def add_action():
    action = sanitize_action(bottle.request.json)
    actions.append(action)

    return action

def sanitize_config(config):
    clean_config = {}
    for opt in ['targets', 'sources']:
        assert opt in config and type(config[opt]) == list, "No {0} present".format(opt)
        clean_config[opt] = [ str(x) for x in config[opt] ]

    return clean_config

def sanitize_event(event):
    assert 'type' in event, "Event missing required field 'type'"
    clean_event = {}

    for k in EVENT_FIELDS:
        if k in event:
            assert type(event[k]) in [str, int, float], "Invalid type for '{0}': {1}".format(k, type(event[k]))
            clean_event[k] = event[k]

    return clean_event

def sanitize_action(action):
    assert 'type' in action, "Action missing required field 'type'"
    clean_action = {}

    for k in ACTION_FIELDS:
        if k in action:
            assert type(action[k]) in [str, int, float], "Invalid type for '{0}': {1}".format(k, type(action[k]))
            clean_action[k] = action[k]

    return clean_action

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
