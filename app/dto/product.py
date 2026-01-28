from pydantic import BaseModel
from typing import Optional


class ProductCreateRequest(BaseModel):
    name: str
    current_price: float
    color_options: str
    network_sp: int
    charge_tech: int
    screen_size: str
    ram: str
    os: str
    chip: str
    memory: str
    pin: int
    sale: Optional[float] = 0.0
    status: Optional[bool] = True
    phone_company: str
    url: Optional[str] = "Không có"
    product_specs: Optional[str] = "Không có"
    product_promotion: Optional[str] = "Không có"


class ProductUpdateRequest(BaseModel):
    product_id: str

    name: Optional[str] = None
    current_price: Optional[float] = None
    color_options: Optional[str] = None
    network_sp: Optional[int] = None
    charge_tech: Optional[int] = None
    screen_size: Optional[str] = None
    ram: Optional[str] = None
    os: Optional[str] = None
    chip: Optional[str] = None
    memory: Optional[str] = None
    pin: Optional[int] = None
    sale: Optional[float] = None
    status: Optional[bool] = None
    phone_company: Optional[str] = None
    url: Optional[str] = None
    product_specs: Optional[str] = None
    product_promotion: Optional[str] = None


class ProductDeleteRequest(BaseModel):
    product_id: str
