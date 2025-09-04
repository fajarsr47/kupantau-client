import os
if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(r"G:\Web\KuPantau\Kupantau_Client\.venv\Lib\site-packages\onnxruntime\capi")

import onnxruntime as ort
os.environ['ORT_LOG_SEVERITY_LEVEL'] = '0'
os.environ['ORT_LOG_VERBOSITY_LEVEL'] = '1'

print("Providers:", ort.get_available_providers())
sess = ort.InferenceSession(
    r"C:\Users\mfaja\.insightface\models\buffalo_l\det_10g.onnx",
    providers=['CUDAExecutionProvider','CPUExecutionProvider']
)
print("Session providers:", sess.get_providers())
