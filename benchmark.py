# utils/benchmark.py

import time
import tracemalloc


def benchmark(predict_function, img_path: str, runs: int = 5):

    tracemalloc.start()

    t0 = time.time()

    for _ in range(runs):

        predict_function(img_path)

    t1 = time.time()

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    return {

        "avg_ms": round((t1 - t0) / runs * 1000, 2),
        "peak_memory_mb": round(peak / (1024 * 1024), 2)

    }


if __name__ == "__main__":

    from ultralytics import YOLO

    model = YOLO("../model/food_yolo_best.pt")

    def predict(img):
        model.predict(img, conf=0.3)

    result = benchmark(predict, "../static/uploads/sample.jpg")

    print("Benchmark Results:")
    print(result)
