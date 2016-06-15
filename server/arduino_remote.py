import bottle

# Just store events and actions in memory for demo
events = []
EVENT_FIELDS = ('type', 'source', 'value', 'current')

actions = []
ACTION_FIELDS = ('type', 'target', 'value', 'processed')

config = {
    'sources': [],
    'targets': []
}

@bottle.route('/')
def index():
    return '<h1>Arduino remote</h1>'

@bottle.route('/config', method='GET')
def show_config():
    return config

@bottle.route('/config', method='POST')
def set_config():
    print("----" + str(bottle.request.json))
    config = sanitize_config(bottle.request.json)

    return config

@bottle.route('/events', method='GET')
def list_events():
    found_events = events
    found_events = [ event for event in events if event.getdefault('current', True) ]
    for event in found_events:
        event['current'] = False

    return dict(events=found_events)

@bottle.route('/events', method='POST')
def add_event():
    event = sanitize_event(bottle.request.json)
    event['current'] = True

    events.append(event)

    return event

@bottle.route('/actions', method='GET')
def list_actions():
    current_actions = [ action for action in actions if action.getdefault('processed', False) ]
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
    bottle.run(host='localhost', port=8080, debug=True)
