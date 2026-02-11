FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
#ENV BOKEH_WEB_SOCKET_MAX_MESSAGE_SIZE=524288000
#ENV PANEL_MAX_UPLOAD_SIZE=524288000

WORKDIR /app

# (Optionnal but recommanded) non-root user
RUN useradd -m appuser

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Code
COPY . /app

# Create writable cache dirs BEFORE dropping privileges
RUN mkdir -p /home/appuser/.cache /tmp/panel \
 && chown -R appuser:appuser /home/appuser /app /tmp/panel

# Port (informative)
EXPOSE 43100

USER appuser

CMD ["panel", "serve", "app.py", "--address", "0.0.0.0", "--port", "43100",  "--allow-websocket-origin", "*", "--index", "app", "--websocket-max-message-size","1073741824"]