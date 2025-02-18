from fastapi import FastAPI
import subprocess 
import json
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def root():
    logger.info("root endpoint called")
    return {"message": "KRR API!", "docs": "/docs"}

@app.get("/run")
async def run(
    kubeconfig_file: str,
    strategy: str,
    prometheus_url: str,
    prometheus_headers: str,
    history_duration: str,
    namespace: str,
    formatter: str,
    extra_args: str = ""
):
    
    try:
        command = [
            "python3", "krr.py", strategy,
            "--kubeconfig", f"./{kubeconfig_file}",
            "--prometheus-url", prometheus_url,
            "--prometheus-headers", prometheus_headers,
            "--openshift",
            f"--history-duration={history_duration}",
            "--namespace", namespace,
            "--formatter", formatter, "-q"
        ]

        if extra_args:
            command.append(extra_args)

        logger.info("Running command: %s", command)

        result = subprocess.run(command, capture_output=True, text=True, check=True)

        stdout_json = json.loads(result.stdout)

        return stdout_json

    except subprocess.CalledProcessError as e:
        logger.error("Command failed with error: %s", e)
        return {"error": str(e), "stderr": e.stderr, "stdout": e.stdout}