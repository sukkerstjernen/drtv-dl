SUPPRESS_OUTPUT = False
PROXY = None

def set_suppress_output(suppress):
    global SUPPRESS_OUTPUT
    SUPPRESS_OUTPUT = suppress

def set_proxy(proxy):
    from drtv_dl.utils.helpers import print_to_screen
    print_to_screen(f"Setting proxy to {proxy}")
    global PROXY
    if '@' in proxy:
        auth, address = proxy.split('@')
        PROXY = {
            'http': f'http://{auth}@{address}',
            'https': f'http://{auth}@{address}'
        }
    else:
        PROXY = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }