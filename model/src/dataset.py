import torch
from torch.utils.data import Dataset, DataLoader

class SequenceDataset(Dataset):
    def __init__(self, data_tensor):
        self.data = data_tensor.astype('float32') if hasattr(data_tensor, 'astype') else data_tensor
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = torch.tensor(self.data[idx])
        return sample, sample
    
def get_dataloader(data, batch_size, num_workers=2):
    dataset = SequenceDataset(data)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)