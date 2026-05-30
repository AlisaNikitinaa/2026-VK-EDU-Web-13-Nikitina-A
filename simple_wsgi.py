def application(environ, start_response):
    # GET параметры
    query_string = environ.get('QUERY_STRING', '')
    get_params = {}
    if query_string:
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                get_params[key] = value

    # POST параметры
    post_params = {}
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    if content_length > 0:
        body = environ['wsgi.input'].read(content_length).decode('utf-8')
        for param in body.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                post_params[key] = value

    # HTML ответ
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Simple WSGI</title></head>
    <body>
        <h1>Simple WSGI App</h1>
        <h2>GET параметры:</h2>
        <ul>
            {''.join(f'<li><b>{k}</b> = {v}</li>' for k, v in get_params.items()) or '<li>нет</li>'}
        </ul>
        <h2>POST параметры:</h2>
        <ul>
            {''.join(f'<li><b>{k}</b> = {v}</li>' for k, v in post_params.items()) or '<li>нет</li>'}
        </ul>
        <hr>
        <form method="POST">
            <input name="test_post" value="hello">
            <button type="submit">Отправить POST</button>
        </form>
    </body>
    </html>
    """.encode('utf-8')

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))),
    ]
    start_response(status, headers)
    return [html]