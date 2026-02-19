#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "panel-graphic-walker",
#   "openpyxl",
#   "fastparquet",
#   "requests"
# ]
# ///
import io
from pathlib import Path

import pandas as pd
import panel as pn
import requests

from panel_gwalker import GraphicWalker

pn.extension()
pn.config.raw_css.append(
    """
    :root {
      --app-bg: #f4f7f8;
      --card-bg: #ffffff;
      --text-main: #1f2933;
      --muted: #52606d;
      --accent: #0f766e;
      --accent-2: #0b5d57;
      --border: #d9e2ec;
    }

    body, .bk-root {
      background: linear-gradient(160deg, #f8fbfc 0%, var(--app-bg) 100%);
      color: var(--text-main);
    }

    .panel-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
      padding: 14px;
    }

    .app-title h1 {
      margin: 0;
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: #102a43;
    }

    .app-subtitle {
      margin: 4px 0 0 0;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .bk-btn-primary {
      background-color: var(--accent) !important;
      border-color: var(--accent) !important;
    }

    .bk-btn-primary:hover {
      background-color: var(--accent-2) !important;
      border-color: var(--accent-2) !important;
    }
    
    .bk-panel-models-esm-ReactComponent {
      width: 100%;
    }
    """
)

# widgets
file_input = pn.widgets.FileInput(accept=".csv,.json,.xlsx,.parquet", multiple=False)
url_input = pn.widgets.TextInput(name="File URL", placeholder="Enter CSV/JSON/XLSX/PARQUET file URL...")
load_button = pn.widgets.Button(name="Load file", button_type="primary")
status = pn.pane.Markdown("")
output = pn.Column(sizing_mode="stretch_both")

def get_data_from_file(file, filename=""):
    if file is not None:
        fname = Path(filename).suffix.lower()
        if fname in (".csv",):
            return pd.read_csv(io.BytesIO(file))
        elif fname in (".json",):
            return pd.read_json(io.BytesIO(file))
        elif fname in (".xlsx", ".xls"):
            return pd.read_excel(io.BytesIO(file))
        elif fname in (".parquet", ".pq"):
            return pd.read_parquet(io.BytesIO(file))
        else:
            raise ValueError(f"Unsupported file format: {fname}")

def _load_action(event=None):
    status.object = ""
    output[:] = []
    
    if file_input.value:
        try:
            df = get_data_from_file(file_input.value, getattr(file_input, "filename", ""))
        except Exception as e:
            status.object = f"**Error reading uploaded file:** {e}"
            return
    elif url_input.value:
        try:
            resp = requests.get(url_input.value, timeout=300)
            resp.raise_for_status()
            fname = Path(url_input.value.split("?", 1)[0]).suffix.lower()
            if fname in (".csv",):
                df = pd.read_csv(io.BytesIO(resp.content))
            elif fname in (".json",):
                df = pd.read_json(io.BytesIO(resp.content))
            elif fname in (".xlsx", ".xls"):
                df = pd.read_excel(io.BytesIO(resp.content))
            elif fname in (".parquet", ".pq"):
                df = pd.read_parquet(io.BytesIO(resp.content))
            else:
                raise ValueError(f"Unsupported file format: {fname}")
        except Exception as e:
            status.object = f"**Error fetching/reading URL:** {e}"
            return
    else:
        status.object = "**No file or URL provided.**"
        return

    try:
        output[:] = [GraphicWalker(df)]
        status.object = f"Loaded {len(df)} rows and {len(df.columns)} columns."
    except Exception as e:
        status.object = f"**Error creating GraphicWalker:** {e}"

load_button.on_click(_load_action)

# Header
header = pn.pane.HTML(
    """
    <div class="app-title">
      <h1>Dataviz with PyGWalker library</h1>
      <p class="app-subtitle">Upload a file or load from URL to start exploring your data.</p>
    </div>
    """
)

# Sidebar with inputs
sidebar = pn.Column(
    pn.pane.Markdown("### Load Data"),
    file_input,
    url_input,
    load_button,
    css_classes=["panel-card"],
    sizing_mode="fixed",
    width=320,
)

# Main content (status + graphic walker output) set to stretch full width
main = pn.Column(
    status,
    output,
    css_classes=["panel-card"],
    sizing_mode="stretch_both",
)

# App layout with a true template sidebar and responsive main area
template = pn.template.BootstrapTemplate(
    title="Humatheque Tiny Dataviz app",
    main_max_width="100%",
)
template.sidebar.append(sidebar)
template.main.append(pn.Column(header, main, sizing_mode="stretch_both"))
app = template
template.servable()

MAX_SIZE_MB = 150

if __name__ == "__main__":
    pn.serve(app, start=True, show=True, websocket_max_message_size=MAX_SIZE_MB * 1024 * 1024, http_server_kwargs={'max_buffer_size': MAX_SIZE_MB * 1024 * 1024})
