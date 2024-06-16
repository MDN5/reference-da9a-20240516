import os
import subprocess
import platform
import webbrowser

def run_mlflow_ui():
    try:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING"] = "true"

        # Determine the appropriate null device based on the platform
        null_device = "/dev/null" if platform.system() != "Windows" else "NUL"
        
        # Run MLflow UI using the subprocess module in the background
        subprocess.Popen(["mlflow", "ui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("MLflow UI server is running in the background.\n You can access it at http://localhost:5000")
        webbrowser.open("http://localhost:5000")

    except Exception as e:
        print(f"Error: {e}")

def stop_mlflow():
    try:
        subprocess.run(["fuser", "-k", "5000/tcp"])
        print("MLflow server stopped.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run_mlflow_ui()






