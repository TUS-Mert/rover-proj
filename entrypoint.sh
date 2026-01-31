#!/bin/sh
echo "🛠 Initializing Database..."
uv run init_db.py 

echo "🚀 Starting Flask..."
exec uv run flask run --host=0.0.0.0