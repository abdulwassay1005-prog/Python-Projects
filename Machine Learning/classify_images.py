from imageai.Classification import ImageClassification
import os
import sys

def main():
    exec_path = os.getcwd()

    # Path to model weights
    weights_path = os.path.join(exec_path, "mobilenet_v2-b0353104.pth")
    if not os.path.isfile(weights_path):
        sys.exit("ERROR: mobilenet_v2-b0353104.pth not found in folder!")

    # Initialize classifier
    classifier = ImageClassification()
    classifier.setModelTypeAsMobileNetV2()
    classifier.setModelPath(weights_path)
    classifier.loadModel()

    # Images to classify
    images = ["house.jpg", "godzilla.jpg", "giraffe.jpg"]

    for img_name in images:
        img_path = os.path.join(exec_path, img_name)
        if not os.path.isfile(img_path):
            print(f"SKIP: {img_name} not found.")
            continue

        print(f"\n----- Top-5 for {img_name} -----")
        predictions, probabilities = classifier.classifyImage(img_path, result_count=5)
        for label, prob in zip(predictions, probabilities):
            print(f"{label:<25} : {prob:6.2f}%")

if __name__ == "__main__":
    main()
