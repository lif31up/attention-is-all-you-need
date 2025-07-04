from torch import nn
from transformers import BertTokenizer, BertModel
from model.Stacks import EncoderStack

class BERT(nn.Module):
  def __init__(self, config, init_weights=None):
    super(BERT, self).__init__()
    self.stacks = nn.ModuleList([EncoderStack(config, init_weights=init_weights) for _ in range(config["n_stack"])])
    self.fc, self.flatten = nn.Linear(393216, config["oupt_dim"], bias=config["bias"]), nn.Flatten(1)
  # __init__():

  def forward(self, x):
    for stack in self.stacks: x = stack(x)
    return self.fc(self.flatten(x))
  # forward()
# BERT

if __name__ == "__main__":
  from datasets import load_dataset
  from torch.utils.data import DataLoader
  from config import CONFIG
  from BPEDataset import BPEDataset

  tokenizer_config, model_config = CONFIG["tokenizer_config"], CONFIG["model"]
  dataset = load_dataset('imdb')['train'].shuffle(seed=42).select(range(10))
  bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
  bert_tokenizer.truncation_side = "right"
  bert_tokenizer.padding_side = "right"
  bert_tokenizer.pad_token = bert_tokenizer.eos_token = "[PAD]"
  bert_model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True, output_attentions=False)
  trainset = BPEDataset(dataset=dataset, dim=model_config["dim"], tokenizer=bert_tokenizer, model=bert_model)

  vurt = BERT(model_config, init_weights=None)

  for feature, label in DataLoader(trainset, batch_size=2, shuffle=True, pin_memory=True, num_workers=1):
    output = vurt(feature)
    print(f"Feature shape: {feature.shape}, Label shape: {label.shape}")
    print(f"Output shape: {output.shape}")
    break  # Just to check the first batch
# if __name__ == "__main__":