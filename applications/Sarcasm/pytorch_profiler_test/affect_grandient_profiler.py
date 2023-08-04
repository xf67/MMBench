from torch import nn
import torch
import sys
import os

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))



from models.eval_scripts.complexity import  all_in_one_train, all_in_one_test
import training_structures # noqa
from training_structures.gradient_blend import train, test # noqa
from unimodals.common_models import GRU, MLP, Transformer # noqa
from datasets.affect.get_data import get_dataloader # noqa
from fusions.common_fusions import Concat # noqa

if __name__ == '__main__':
# mosi_data.pkl, mosei_senti_data.pkl
# mosi_raw.pkl, mosei_senti_data.pkl, sarcasm.pkl, humor.pkl
# raw_path: mosi.hdf5, mosei.hdf5, sarcasm_raw_text.pkl, humor_raw_text.pkl
    traindata, validdata, test_robust = \
        get_dataloader('C:/Users/29296/Documents/Tencent Files/2929629852/FileRecv/sarcasm.pkl',
                   task='classification', robust_test=False, max_pad=True,data_type='sarcasm')

# mosi/mosei
# encoders = [Transformer(35, 70).cuda(),
#             Transformer(74, 150).cuda(),
#             Transformer(300, 600).cuda()]
# head = MLP(820, 512, 2).cuda()
#
# unimodal_heads = [MLP(70, 32, 2).cuda(), MLP(
#     150, 64, 2).cuda(), MLP(600, 256, 2).cuda()]

#humor/sarcasm
    encoders=[Transformer(371,700).cuda(), \
        Transformer(81,150).cuda(),\
        Transformer(300,600).cuda()]
    head=MLP(1450,512,2).cuda()

    unimodal_heads=[MLP(700,512,2).cuda(),MLP(150,64,2).cuda(),MLP(600,256,2).cuda()]

    fusion = Concat().cuda()

# training_structures.gradient_blend.criterion = nn.L1Loss()
# 可以使用
    with torch.profiler.profile(
            activities=[
            torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA,
        ]
    ) as p:
        train(encoders, head, unimodal_heads, fusion, traindata, validdata, 100, gb_epoch=20, lr=1e-3, AUPRC=False,
          classification=True, optimtype=torch.optim.AdamW, savedir='mosi_best_gb.pt', weight_decay=0.1)
    print(p.key_averages().table(
        sort_by="self_cuda_time_total", row_limit=-1))

    #train(encoders, head, unimodal_heads, fusion, traindata, validdata, 100, gb_epoch=20, lr=1e-3, AUPRC=False,
     # classification=True, optimtype=torch.optim.AdamW, savedir='mosi_best_gb.pt', weight_decay=0.1)

    print("Testing:")
    model = torch.load('mosi_besf_gb.pt').cuda()

    test(model, test_robust, dataset='mosi', auprc=False, no_robust=True)

# test(model=model, test_dataloaders_all=test_robust, dataset='mosi', is_packed=True, criterion=torch.nn.L1Loss(), task='posneg-classification')