import os
import torch
import cv2

from mtcnn import MTCNN
from keras_facenet import FaceNet


mtcnn = MTCNN()
facenet = FaceNet()


def extract_embedding(image_path):

    img = cv2.imread(image_path)

    img = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )


    faces = mtcnn.detect_faces(img)

    if len(faces) == 0:
        return None


    x, y, w, h = faces[0]["box"]

    x = max(0, x)
    y = max(0, y)

    face = img[
        y:y+h,
        x:x+w
    ]


    embedding = facenet.embeddings(
        [face]
    )[0]


    return torch.tensor(
        embedding,
        dtype=torch.float32
    )



def create_embeddings(
    image_dir,
    output_file
):

    data = []


    for file in os.listdir(image_dir):

        path = os.path.join(
            image_dir,
            file
        )


        embedding = extract_embedding(
            path
        )


        if embedding is not None:

            data.append(
                embedding
            )


            print(
                "OK:",
                file
            )

        else:
            print(
                "No Face:",
                file
            )


    data = torch.stack(data)


    torch.save(
        data,
        output_file
    )


    print(
        "Saved:",
        output_file
    )



create_embeddings(
    "images/accept",
    "embeddings/accept.pt"
)


#create_embeddings(
#    "images/reject",
#    "embeddings/reject.pt"
#)
