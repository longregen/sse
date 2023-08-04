import torch
from torch import Tensor
from transformers import AutoModel

import sys

from .tokenizer import tokenizer

print ('» loading model e5-large-v2...', file=sys.stderr)
# Check if a GPU is available and if not, use the CPU
DEV = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

model = AutoModel.from_pretrained('/data/models/e5-large-v2').to(DEV)
print ('» loaded e5-large-v2 OK', file=sys.stderr)

def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

def embed(phrase):
    tokenized = tokenizer([phrase], padding=True, truncation='only_first', return_tensors='pt').to(DEV)
    outputs = model(**tokenized)
    return average_pool(outputs.last_hidden_state, tokenized['attention_mask'])[0].tolist()

