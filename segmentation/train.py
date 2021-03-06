import argparse

from segmentation.dataset import NerveSegmentationDataset
from segmentation.transform import preprocessing
from segmentation.model import U_Net, R2U_Net, AttU_Net, R2AttU_Net
from segmentation.loss import dice_loss, tversky_loss
from segmentation.metric import dice_coeff, tversky
from segmentation.trainer import Trainer

import torch
from torch.utils.data import DataLoader


parser = argparse.ArgumentParser()
parser.add_argument(
    '--batch_size', type=int, default=2
)
parser.add_argument(
    '--epoch', type=int, default=40
)
parser.add_argument(
    '--lr', type=float, default=0.001
)
parser.add_argument(
    '--dataset', type=str, default='./data/'
)
parser.add_argument(
    '--workers', type=int, default=4
)
parser.add_argument(
    '--save_model', type=str, default='./save_model/'
)

cfg = parser.parse_args()
print(cfg)

device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
print(device)

if __name__ == "__main__":
    ds_train = NerveSegmentationDataset(root='./data/', no_mask=False, train=True, transform=preprocessing)
    ds_test = NerveSegmentationDataset(root='./data/', no_mask=False, train=False, transform=preprocessing)
    dl_train = DataLoader(ds_train, batch_size=cfg.batch_size, shuffle=True, num_workers=cfg.workers)
    dl_test = DataLoader(ds_test, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.workers)

    print("DATA LOADED")
    model = U_Net()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    criterion = tversky_loss
    success_metric = tversky

    trainer = Trainer(model, criterion, optimizer, success_metric, device, None)
    fit = trainer.fit(dl_train, dl_test, num_epochs=cfg.epoch, checkpoints=cfg.save_model+model.__class__.__name__+'.pt')
    torch.save(model.state_dict(), './seg/final_state_dict.pt')
    torch.save(model, './seg/final.pt')

    loss_fn_name = "dice_loss"
    best_score = str(fit.best_score)
    print(f"Best loss score(loss function = {loss_fn_name}): {best_score}")
