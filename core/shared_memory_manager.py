from multiprocessing import shared_memory
import numpy as np
import json

class SharedMemoryManager:
    def __init__(self, size: int):
        """Inicializa un bloque de memoria compartida de un tamaño específico."""
        self.shm = shared_memory.SharedMemory(create=True, size=size)
        self.data = np.ndarray((size,), dtype=np.uint8, buffer=self.shm.buf)  # Usamos uint8 para almacenar los datos
        self.size = size

    def write(self, data):
        """Escribe datos en la memoria compartida."""
        json_data = json.dumps(data).encode('utf-8')
        self.data[:len(json_data)] = np.frombuffer(json_data, dtype=np.uint8)

    def read(self):
        """Lee datos desde la memoria compartida."""
        json_data = bytes(self.data[:self.size]).decode('utf-8')
        return json.loads(json_data)

    def release(self):
        """Libera la memoria compartida."""
        self.shm.close()
        self.shm.unlink()
