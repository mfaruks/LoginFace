from keyboard import type_text 
import sys
import os
import hashlib
import cv2
import torch
import torch.nn as nn

from getpass import getpass
from mtcnn import MTCNN
from keras_facenet import FaceNet

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class BitGeneratorNet(nn.Module):

    def __init__(self, input_dim):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(512, 256)
        )


    def forward(self, x):

        return self.network(x)



def generate_aes_key(model, embedding):

    model.eval()

    with torch.no_grad():

        logits = model(embedding)

        bits = (
            torch.sigmoid(logits) > 0.5
        ).int()


    bit_string = ''.join(
        map(str, bits[0].tolist())
    )


    key_bytes = int(
        bit_string,
        2
    ).to_bytes(
        32,
        byteorder="big"
    )


    return hashlib.sha256(
        key_bytes
    ).digest()



def encrypt(model, embedding, data, output_file):

    key = generate_aes_key(
        model,
        embedding
    )

    aes = AESGCM(key)

    nonce = os.urandom(12)


    encrypted = aes.encrypt(
        nonce,
        data.encode(),
        None
    )


    with open(output_file, "wb") as f:

        f.write(nonce)
        f.write(encrypted)


    print(
        f"Encryption completed: {output_file}"
    )



def decrypt(model, embedding, input_file):

    key = generate_aes_key(
        model,
        embedding
    )


    with open(input_file, "rb") as f:

        nonce = f.read(12)
        encrypted = f.read()


    aes = AESGCM(key)


    decrypted = aes.decrypt(
        nonce,
        encrypted,
        None
    )


    print(
        decrypted.decode()
    )



mtcnn = MTCNN()
facenet = FaceNet()



def get_live_embedding():

    cap = cv2.VideoCapture(0)


    if not cap.isOpened():

        raise RuntimeError(
            "Could not open camera"
        )


    try:

        while True:

            ret, frame = cap.read()


            if not ret:
                continue


            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


            faces = mtcnn.detect_faces(rgb)


            if len(faces) > 0:

                x, y, w, h = faces[0]["box"]


                x = max(0, x)
                y = max(0, y)


                face = rgb[
                    y:y+h,
                    x:x+w
                ]


                embedding = facenet.embeddings(
                    [face]
                )[0]


                return torch.tensor(
                    embedding,
                    dtype=torch.float32
                ).unsqueeze(0)


    finally:

        cap.release()



def main():

    try:

        if len(sys.argv) != 2:

            print(
                "Usage: python decrypt.py [0|1|live]"
            )

            sys.exit(1)



        mode = sys.argv[1]


        if mode not in ["0", "1", "live"]:

            print(
                "Invalid mode. Use 0 for encrypt, 1 for decrypt, live for typing."
            )

            sys.exit(1)



        model = BitGeneratorNet(512)


        model.load_state_dict(
            torch.load(
                "face_bit_model.pth",
                map_location="cpu"
            )
        )


        model.eval()


        print(
            "Waiting for face..."
        )


        embedding = get_live_embedding()


        if embedding is None:

            print(
                "Face not detected."
            )

            sys.exit(1)



        if mode == "0":


            data1 = getpass(
                "Enter data to encrypt: "
            )


            data2 = getpass(
                "Confirm data: "
            )


            if data1 != data2:

                print(
                    "Data does not match."
                )

                sys.exit(1)



            encrypt(
                model,
                embedding,
                data1,
                "secret.bin"
            )



        elif mode == "1":


            decrypt(
                model,
                embedding,
                "secret.bin"
            )



        elif mode == "live":


            key = generate_aes_key(
                model,
                embedding
            )


            with open("secret.bin", "rb") as f:

                nonce = f.read(12)
                encrypted = f.read()


            aes = AESGCM(key)


            data = aes.decrypt(
                nonce,
                encrypted,
                None
            ).decode()


            type_text(
                data
            )



    except FileNotFoundError as e:

        print(
            f"File not found: {e}"
        )


    except InvalidTag:

        print(
            "Decryption failed: wrong face or invalid encrypted data."
        )


    except RuntimeError as e:

        print(
            f"Runtime error: {e}"
        )


    except KeyboardInterrupt:

        print(
            "\nOperation cancelled by user."
        )


    except Exception as e:

        print(
            f"Unexpected error: {e}"
        )



if __name__ == "__main__":

    main()
