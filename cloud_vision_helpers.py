import cv2
import os
import io
from google.cloud import vision

"""
Wrapper class for Google Vision API calls working with OpenCV to detect labels and to detect faces
"""


class cloud_vision_helpers:
    """
    Constructor for cloud_vision object
    """

    def __init__(self):
        self.labels = None

    """
    Method for detecting labels from Google API documents
    @param path: A string indicating the location in a system to write to upon taking a photo
    """

    def detect_label(self, path):

        # Imports the Google Cloud client library

        # Instantiates a client
        client = vision.ImageAnnotatorClient()

        # The name of the image file to annotate
        file_name = path

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations

        print('Labels:')
        for label in labels:
            print(label.description)
            self.labels = label.description

    """
    Method for detecting faces and emotions from Google API documents
    @param path: A string indicating the location in a system to write to upon taking a photo
    """
    @staticmethod
    def detect_faces(path):
        """Detects faces in an image."""
        from google.cloud import vision
        import io
        client = vision.ImageAnnotatorClient()

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.face_detection(image=image)
        faces = response.face_annotations

        # Names of likelihood from google.cloud.vision.enums
        likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                           'LIKELY', 'VERY_LIKELY')
        print('Faces:')

        for face in faces:
            print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
            print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
            print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                         for vertex in face.bounding_poly.vertices])

            print('face bounds: {}'.format(','.join(vertices)))

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

    def getlabels(self):
        return self.labels


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    directory = r'/home/chrischang5/PycharmProjects/SFHACKS2021'
    os.chdir(directory)
    CV1 = cloud_vision_helpers()

    while True:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('l'):
            cv2.imwrite('file.jpg', frame)
            CV1.detect_label('/home/chrischang5/PycharmProjects/SFHACKS2021/file.jpg')

        if cv2.waitKey(1) & 0xFF == ord('f'):
            cv2.imwrite('file.jpg', frame)
            CV1.detect_faces(r'C:\Users\caleb\Pictures\test\file.jpg')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
