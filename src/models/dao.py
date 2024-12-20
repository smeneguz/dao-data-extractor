# src/models/dao.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Contract:
    address: str
    type: str
    name: str
    deployed_at: Optional[int] = None

    def __post_init__(self):
        self.address = self.address.lower()
        if not self.address.startswith('0x'):
            raise ValueError("Contract address must start with '0x'")

@dataclass
class DAO:
    name: str
    description: str
    contracts: List[Contract]
    chain_id: int