"""Development and production WSGI entry point."""

import os

from app import create_app

if __name__ == "__main__":
    print("Starting API and connecting to MongoDB...", flush=True)

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    if os.environ.get("APP_ENV") == "production":
        from waitress import serve

        print(f"Production API listening at http://{host}:{port}", flush=True)
        serve(app, host=host, port=port)
    else:
        app.run(host=host, port=port, debug=True)
