import time
import logging
from functools import wraps

# Configura el logger global
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

NODE_TIMES = {}

def timed_node(fn):
    """Decorador para medir el tiempo y registrar logs de cada nodo."""
    @wraps(fn)
    def wrapper(state, *args, **kwargs):
        node_name = fn.__name__
        logging.info(f"▶️ Entrando al nodo: {node_name}")
        start = time.time()

        try:
            result = fn(state, *args, **kwargs)
        except Exception as e:
            logging.error(f"❌ Error en nodo {node_name}: {e}")
            raise

        elapsed = round(time.time() - start, 2)
        NODE_TIMES[node_name] = elapsed
        logging.info(f"⏱️ Nodo {node_name} tardó {elapsed} segundos")
        return result
    return wrapper


def log_summary():
    """Imprime un resumen al final de los tiempos por nodo."""
    if NODE_TIMES:
        logging.info("\n📊 Resumen de tiempos por nodo:")
        for name, secs in NODE_TIMES.items():
            logging.info(f"   {name:<20} → {secs:5.2f} s")
