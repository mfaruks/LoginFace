# LoginFace

LoginFace is a face-based authentication system that generates a unique AES encryption key from face embeddings using a neural network.

The system workflow:

- Captures a face image from the camera.
- Detects the face region using MTCNN.
- Generates a face embedding using FaceNet.
- Uses a neural network to generate a 256-bit key.
- Uses the generated key for AES-GCM encryption and decryption.

---

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Add your face images

First, create the following directory:

```
images/
└── accept/
```

Add your own face images inside the `accept` directory.

It is recommended to add at least 15 different images for better accuracy.

For better results, use images with:

- Different angles
- Different lighting conditions
- Different facial expressions
- Different distances from the camera

Example:

```
images/
└── accept/
    ├── face1.jpg
    ├── face2.jpg
    ├── face3.jpg
    ├── face4.jpg
    └── ...
```

### 2. Generate face embeddings

Run:

```bash
python embedding.py
```

This step processes your face images. The program:

- Reads images from `images/accept`.
- Detects faces using MTCNN.
- Generates embeddings using FaceNet.
- Saves the generated embeddings.

After completion, the following file will be created:

```
embeddings/
└── accept.pt
```

### 3. Generate the neural network model

Run:

```bash
python generate_model.py
```

This step trains the neural network using the generated face embeddings.

The model learns to generate a 256-bit output from your face embedding.

After training finishes, `face_bit_model.pth` will be created. This file contains the trained neural network.

---

## Encryption

To encrypt your password or private data:

```bash
python decrypt.py 0
```

The program will:

- Open the camera in the background.
- Capture your face.
- Generate a face embedding.
- Generate a 256-bit key using the neural network.
- Ask you to enter your password securely.
- Encrypt the password using AES-GCM.
- Save the encrypted data.

The encrypted file will be: `secret.bin`

Your password is never stored as plain text.

---

## Decryption

To decrypt your stored password/data:

```bash
python decrypt.py 1
```

The program will:

- Capture your face from the camera.
- Generate the same 256-bit key.
- Use the key to decrypt `secret.bin`.
- Print the original password/data.

If another person tries to decrypt the data, the generated key will be different and decryption will fail.

---

## Automatic Keyboard Input

If you want the decrypted password to be automatically typed as keyboard input:

```bash
python decrypt.py live
```

This mode will:

- Verify your face.
- Decrypt the stored password.
- Automatically type the password using keyboard input.

This can be used for automatic login workflows.

---

## Project Structure

```
LoginFace/
│
├── images/
│   └── accept/
│       ├── face1.jpg
│       ├── face2.jpg
│       └── ...
│
├── embeddings/
│   └── accept.pt
│
├── embedding.py
├── generate_model.py
├── decrypt.py
│
├── face_bit_model.pth
├── secret.bin
│
├── requirements.txt
└── README.md
```
