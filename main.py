import boto3, json, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO

# Detects object labels in an image stored in S3
def detect_labels(photo, bucket):
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=10
    )

    # Print detected labels and confidence
    print("\nDetected labels for:", photo)
    for label in response['Labels']:
        print(f"{label['Name']} ({label['Confidence']:.2f}%)")

    # Load the image from S3 like PNG/JPG
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, photo)
    img_data = obj.get()['Body'].read()
    img = Image.open(BytesIO(img_data))

    # Draw bounding boxes on detected objects
    plt.imshow(img)
    ax = plt.gca()
    for label in response['Labels']:
        for instance in label.get('Instances', []):
            box = instance['BoundingBox']
            left = box['Left'] * img.width
            top = box['Top'] * img.height
            width = box['Width'] * img.width
            height = box['Height'] * img.height
            rect = patches.Rectangle((left, top), width, height, linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect)
            plt.text(left, top-5, label['Name'], color='red', fontsize=10, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    plt.axis('off')
    plt.show()

# Detects celebrity faces in an image using Rekognition
def recognize_celebrities(photo, bucket):
    client = boto3.client('rekognition')
    response = client.recognize_celebrities(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}}
    )

    # Print matched celebrity names and confidence
    print("\nCelebrity faces found in:", photo)
    if response['CelebrityFaces']:
        for celeb in response['CelebrityFaces']:
            print(f"→ {celeb['Name']} ({celeb['MatchConfidence']:.2f}%)")
    else:
        print("→ No celebrity match found.")

# Main function: loop through images and execute analysis
def main():
    bucket = 'your-bucket-name'        # <<-- Replace with your S3 bucket name
    images = ['img1.png', 'img2.png']  # <<-- Replace with your filenames
    for img in images:
        detect_labels(img, bucket)
        recognize_celebrities(img, bucket)

if __name__ == "__main__":
    main()
