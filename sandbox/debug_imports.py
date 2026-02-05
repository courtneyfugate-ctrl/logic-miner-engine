
import sys
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

print("\n--- Testing Matplotlib ---")
try:
    import matplotlib
    print(f"Matplotlib Path: {matplotlib.__file__}")
    import matplotlib.pyplot as plt
    print("Matplotlib.pyplot imported successfully")
except Exception as e:
    print(f"Matplotlib Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Testing Plotly ---")
try:
    import plotly
    print(f"Plotly Path: {plotly.__file__}")
    import plotly.graph_objects as go
    print("Plotly.graph_objects imported successfully")
except Exception as e:
    print(f"Plotly Error: {e}")
    import traceback
    traceback.print_exc()
