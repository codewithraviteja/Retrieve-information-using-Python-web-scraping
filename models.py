from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Product:
    name: str
    sku: str
    price: float = None
    sale_price: float = None
    currency: str = None
    images: list = field(default_factory=list)
    description: str = None
    category: str = None
    brand: str = None
    country: str = None
    availability: str = None
    rating: float = None
    reviews: int = None
    sizes: list = field(default_factory=list)
    available_sizes: list = field(default_factory=list)
    colors: list = field(default_factory=list)
    gender: str = None
    url: str = None
    scraped_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_dict(self):
        return {
            'name': self.name,
            'sku': self.sku,
            'price': self.price,
            'sale_price': self.sale_price,
            'currency': self.currency,
            'images': self.images,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'country': self.country,
            'availability': self.availability,
            'rating': self.rating,
            'reviews': self.reviews,
            'sizes': self.sizes,
            'available_sizes': self.available_sizes,
            'colors': self.colors,
            'gender': self.gender,
            'url': self.url,
            'scraped_at': self.scraped_at
        }