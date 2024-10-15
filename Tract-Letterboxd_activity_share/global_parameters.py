import darkdetect

html_errors = {
    '100': 'Continue', 
    '101': 'Switching Protocols', 
    '200': 'OKAction completed successfully', 
    '201': 'CreatedSuccess following a POST command', 
    '202': 'AcceptedRequest has been accepted for processing, but processing has not completed', 
    '203': 'Partial InformationResponse to a GET command; indicates that the returned meta information is from a private overlaid web', 
    '204': 'No ContentServer received the request, but there is no information to send back', 
    '205': 'Reset Content', 
    '206': 'Partial ContentRequested file was partially sent; usually caused by stopping or refreshing a web page', 
    '300': 'Multiple Choices', 
    '301': 'Moved PermanentlyRequested a directory instead of a specific file; the web server added the file name index.html, index.htm, home.html, or home.htm to the URL', 
    '302': 'Moved Temporarily', 
    '303': 'See Other', 
    '304': 'Not ModifiedCached version of the requested file is the same as the file to be sent', 
    '305': 'Use Proxy', 
    '400': 'Bad RequestRequest had bad syntax or was impossible to fulfill', 
    '401': 'UnauthorizedUser failed to provide a valid user name/password required for access to a file/directory', 
    '402': 'Payment Required', 
    '403': 'ForbiddenRequest does not specify the file name, or the directory or the file does not have the permission that allows the pages to be viewed from the web', 
    '404': 'Not FoundRequested file was not found', 
    '405': 'Method Not Allowed', 
    '406': 'Not Acceptable', 
    '407': 'Proxy Authentication Required', 
    '408': 'Request Time-Out', 
    '409': 'Conflict', 
    '410': 'Gone', 
    '411': 'Length Required', 
    '412': 'Precondition Failed', 
    '413': 'Request Entity Too Large', 
    '414': 'Request-URL Too Large', 
    '415': 'Unsupported Media Type', 
    '500': 'Server ErrorIn most cases, this error results from a problem with the code or program you are calling rather than with the web server itself.', 
    '501': 'Not ImplementedServer does not support the facility required', 
    '502': 'Bad Gateway', 
    '503': 'Out of ResourcesServer cannot process the request due to a system overload; should be a temporary condition', 
    '504': 'Gateway Time-OutService did not respond within the time frame that the gateway was willing to wait', 
    '505': 'HTTP Version Not Supported'
}

# detect light modew
def Light_mode(mode):
    global SYSTEM_LIGHT_MODE
    match mode:
        case 'System':
            SYSTEM_LIGHT_MODE = 'Dark' if darkdetect.isDark() else 'Light'
        case 'Light':
            SYSTEM_LIGHT_MODE = 'Light'
        case 'Dark':
            SYSTEM_LIGHT_MODE = 'Dark'
# current direction of the main
CURRENT_DIR = None
# Corner radius for widgets
CORNER_RADIUS = 10
# outer padding (mostly horizontal)
OUTER_PAD = 20
# inner padding (mostly vertical)
INNER_PAD = 10
# padding for same type elements
ELEMENTS_PAD = 5