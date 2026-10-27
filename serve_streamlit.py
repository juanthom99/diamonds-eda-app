import shlex
import subprocess
from pathlib import Path

import modal

app = modal.App(name="diamonds-eda-app")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "streamlit",
        "pandas",
        "matplotlib",
        "seaborn",
        "supabase",
        "python-dotenv",
    )
    .add_local_file(Path(__file__).parent / "app.py", "/root/app.py")
    .add_local_file(Path(__file__).parent / "data_source.py", "/root/data_source.py")
    .add_local_file(Path(__file__).parent / "data" / "diamonds.csv", "/root/data/diamonds.csv")
)

supabase_secret = modal.Secret.from_name("supabase-secret")


@app.function(
    image=image,
    secrets=[supabase_secret],
    min_containers=1,
)
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    target = shlex.quote("/root/app.py")
    cmd = (
        f"streamlit run {target} "
        f"--server.port 8000 "
        f"--server.address 0.0.0.0 "
        f"--server.enableCORS=false "
        f"--server.enableXsrfProtection=false"
    )
    subprocess.Popen(cmd, shell=True)
