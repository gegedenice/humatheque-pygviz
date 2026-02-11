# humatheque-pygviz : Panel / Bokeh Dataviz App — Run Guide

This app is a **Panel** application served by the **Bokeh server**.

## 1) Run with Docker

```bash
docker build -t pigviz:dev .
docker run --name pigviz --rm -p 7860:7860 pigviz:dev
```

## 1) Run without Docker

```
python -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

panel serve app.py \
  --address 0.0.0.0 \
  --port 7860 \
  --index app.py \
  --websocket-max-message-size 524288000
```
Or with uv

```
uv venv
uv pip install -r requirements.txt

uv run app.py
```