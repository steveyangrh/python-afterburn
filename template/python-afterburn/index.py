"""python template for running in afterburn mode"""

import sys
from function import handler

SEPARATOR = "\r\n"

def parse_header():
    """Reads the http headers from watchdog over stdin
    Returns:
        string: http method of the request
        dict: http headers in string to string dictionary
    """
    raw_header = ""
    while True:
        line = read_line()
        if line == "\n":
            break
        raw_header += line

    headers = {}
    method = ''
    for index, header in enumerate(raw_header.split("\n")):
        # Parse the first line to get http method
        if index == 0:
            method = header.split(' ')[0]
            continue
        # Parse rest of the lines for key, value
        parts = header.split(':')
        headers[parts[0]] = ''.join(parts[1:])

    return method, headers

def read_line():
    """Reads the individual line representing header from stdin"""
    line = ""
    while True:
        char = sys.stdin.read(1)
        if char == "\r":
            continue
        line += char
        if char == "\n":
            break
    return line

def get_request():
    """Reads the http request from watchdog over stdin

    Returns:
        string: http method of the request
        dict: http headers in string to string dictionary
        string: http body of the request
    """
    method, headers = parse_header()

    if 'Content-Length' not in headers:
        raise KeyError('Content-Length must be present in the request')

    content_length = int(headers['Content-Length'])
    body = sys.stdin.read(content_length)

    return method, headers, body

def make_response(status, result, content_type=None):
    """Makes the http response

    Returns:
        string: raw response
    """
    response = ""
    # Add headers
    response += "HTTP/1.1 {}{}".format(status, SEPARATOR)
    response += "Content-Length: {}{}".format(len(result), SEPARATOR)
    if content_type:
        response += "Content-Type: {}{}".format(content_type, SEPARATOR)
    response += "Connection: Close{}".format(SEPARATOR)
    # Add separator
    response += SEPARATOR
    # Add body
    response += result

    return response

def parse():
    """
    Reads the incoming request from stdin
    Calls the function with the request body
    Writes the function's response to stdout
    """
    while True:
        try:
            # Get the incoming request
            method, headers, body = get_request()
            # Call the function
            result = handler.handle(body)
            # Make response
            response = make_response("200 OK", result, "text/plain")
        except BaseException as e:
            # Make response
            response = make_response("500", "Internal Error: {}".format(" ".join(e.args)), "text/plain")
        # Write response to stdout
        sys.stdout.write(response)
        sys.stdout.flush()

if __name__ == "__main__":
    parse()
