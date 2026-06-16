import accelerate
print("accelerate", accelerate.__version__, flush=True)
from accelerate import Accelerator
a = Accelerator()
print("accelerator ok, device:", a.device, flush=True)
