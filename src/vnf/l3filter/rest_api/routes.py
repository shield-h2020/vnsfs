import api_calls

route_dictionary = {
    r'^/getRules/v1$': {
        'GET': api_calls.get_rules,
        'media_type': 'application/json'},
    r'^/setRules/v1$': {
        'POST': api_calls.set_rules,
        'media_type': 'application/json'},
    r'^/flushRules/v1$': {
        'DELETE': api_calls.flush_rules,
        'media_type': 'application/json'},
    r'^/flushRule/v1/': {
        'DELETE': api_calls.flush_rule,
        'media_type': 'application/json'}
}


def get_all():
    return route_dictionary
