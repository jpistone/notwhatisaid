import pynvml

pynvml.nvmlInit()
device_count = pynvml.nvmlDeviceGetCount()
print(f"Found {device_count} GPU(s)")

for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    name = pynvml.nvmlDeviceGetName(handle)
    print(f"GPU {i}: {name}")