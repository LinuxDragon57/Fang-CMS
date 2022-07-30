from flask import render_template


def client_errors(e):
    return render_template('routes/clientErrors.html')


def bad_request(e):
    return client_errors(e), 400


def unauthorized(e):
    return client_errors(e), 401


def forbidden(e):
    return client_errors(e), 403


def page_not_found(e):
    return client_errors(e), 404


def method_not_allowed(e):
    return client_errors(e), 405


def request_timeout(e):
    return client_errors(e), 408


def server_errors(e):
    return render_template('routes/serverErrors.html')


def internal_server_error(e):
    return server_errors(e), 500


def bad_gateway(e):
    return server_errors(e), 502


def service_unavailable(e):
    return server_errors(e), 503


def gateway_timeout(e):
    return server_errors(e), 504
