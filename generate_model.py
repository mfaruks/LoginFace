import torch
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader


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



class EmbeddingDataset(Dataset):

    def __init__(self, accept_file, reject_file):

        accept_embeddings = torch.load(
            accept_file
        )

        reject_embeddings = torch.load(
            reject_file
        )


        # Aynı yüz için aynı key
        self.accept_key = torch.randint(
            0,
            2,
            (256,)
        ).float()


        # Reject için farklı sınıf key
        self.reject_key = torch.randint(
            0,
            2,
            (256,)
        ).float()


        self.embeddings = torch.cat(
            [
                accept_embeddings,
                reject_embeddings
            ],
            dim=0
        )


        self.targets = torch.cat(
            [
                self.accept_key.repeat(
                    accept_embeddings.shape[0],
                    1
                ),

                self.reject_key.repeat(
                    reject_embeddings.shape[0],
                    1
                )
            ],
            dim=0
        )


    def __len__(self):

        return len(self.embeddings)


    def __getitem__(self, index):

        return (
            self.embeddings[index],
            self.targets[index]
        )



def train_model(
    model,
    train_loader,
    epochs=50,
    lr=1e-3
):

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )


    model.to(device)


    criterion = nn.BCEWithLogitsLoss()


    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr,
        weight_decay=1e-4
    )


    for epoch in range(epochs):

        model.train()

        total_loss = 0


        for x, y in train_loader:


            x = x.to(device)
            y = y.to(device)


            optimizer.zero_grad()


            output = model(x)


            loss = criterion(
                output,
                y
            )


            loss.backward()


            optimizer.step()


            total_loss += loss.item()



        avg_loss = (
            total_loss /
            len(train_loader)
        )


        print(
            f"Epoch {epoch+1}/{epochs} "
            f"Loss: {avg_loss:.5f}"
        )



# Dataset

dataset = EmbeddingDataset(
    "embeddings/accept.pt",
    "embeddings/reject.pt"
)


loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True
)



# Model

model = BitGeneratorNet(
    input_dim=512
)


train_model(
    model,
    loader,
    epochs=50
)



# Kaydet

torch.save(
    model.state_dict(),
    "face_bit_model.pth"
)


print(
    "Model Saved."
)
