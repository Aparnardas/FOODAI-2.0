import tensorflow as tf
import os


def convert_quant(model_path, output_path):

    """
    Convert Keras model to TFLite INT8 quantized model
    """

    print("Loading model...")

    model = tf.keras.models.load_model(model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:

        f.write(tflite_model)

    print(f"Quantized model saved: {output_path}")


if __name__ == "__main__":

    convert_quant(
        "model/mobilenet_food.h5",
        "model/mobilenet_food_int8.tflite"
    )
