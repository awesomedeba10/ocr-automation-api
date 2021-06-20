from app import app

app.run(host=app.config.get('APP_HOST', '127.0.0.1'),
    port=app.config.get('APP_PORT', 5000),
    debug=app.config.get('APP_DEBUG', False))