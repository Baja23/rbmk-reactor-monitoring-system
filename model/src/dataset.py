import torch
from torch.utils.data import IterableDataset, DataLoader, get_worker_info

class SequenceDataset(IterableDataset):
    def __init__(self, data_tensor):
        self.data = data_tensor.astype('float32') if hasattr(data_tensor, 'astype') else data_tensor
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            # Single-process data loading
            for idx in range(len(self.data)):
                sample = torch.tensor(self.data[idx])
                yield sample, sample
        else:
            # Multi-process data loading
            chunk_size = len(self.data) // worker_info.num_workers
            start_idx = worker_info.worker_id * chunk_size
            if worker_info.worker_id == worker_info.num_workers - 1:
                end_idx = len(self.data)
            else:
                end_idx = start_idx + chunk_size
            for idx in range(start_idx, end_idx):
                sample = torch.tensor(self.data[idx])
                yield sample, sample

def get_dataloader(data, batch_size, num_workers=2):
    dataset = SequenceDataset(data)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)