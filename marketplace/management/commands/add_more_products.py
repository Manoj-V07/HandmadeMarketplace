from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Adds more sample products to the database'

    def handle(self, *args, **kwargs):
        # Get admin user
        admin_user = User.objects.get(username='ManojV')
        
        # Create or get categories
        categories = {
            'Electronics': 'Modern electronic gadgets and accessories',
            'Fashion': 'Trendy clothing and accessories',
            'Home & Kitchen': 'Essential items for your home',
            'Books': 'Best-selling books and stationery',
            'Sports': 'Sports equipment and accessories',
            'Beauty': 'Beauty and personal care products',
            'Toys': 'Fun toys and games for all ages',
            'Garden': 'Gardening tools and plants',
        }
        
        created_categories = {}
        for name, description in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            created_categories[name] = category
            if created:
                self.stdout.write(f'Created category: {name}')
        
        # Sample products data
        products_data = [
            {
                'name': 'Wireless Bluetooth Earbuds',
                'description': 'High-quality wireless earbuds with noise cancellation and 24-hour battery life.',
                'price': Decimal('79.99'),
                'stock': 50,
                'category': 'Electronics',
                'additional_details': 'Bluetooth 5.0\nWater resistant\nIncludes charging case'
            },
            {
                'name': 'Smart Watch Series 5',
                'description': 'Feature-rich smartwatch with health monitoring and GPS tracking.',
                'price': Decimal('199.99'),
                'stock': 30,
                'category': 'Electronics',
                'additional_details': 'Heart rate monitor\nSleep tracking\nWater resistant to 50m'
            },
            {
                'name': 'Designer Leather Wallet',
                'description': 'Genuine leather wallet with multiple card slots and RFID protection.',
                'price': Decimal('49.99'),
                'stock': 100,
                'category': 'Fashion',
                'additional_details': 'Genuine leather\n6 card slots\nRFID blocking'
            },
            {
                'name': 'Stainless Steel Cookware Set',
                'description': '10-piece stainless steel cookware set with non-stick coating.',
                'price': Decimal('149.99'),
                'stock': 25,
                'category': 'Home & Kitchen',
                'additional_details': '10 pieces\nDishwasher safe\nOven safe up to 500°F'
            },
            {
                'name': 'Bestselling Novel Collection',
                'description': 'Set of 5 bestselling novels in hardcover edition.',
                'price': Decimal('89.99'),
                'stock': 40,
                'category': 'Books',
                'additional_details': '5 hardcover books\nIncludes popular titles\nGift box included'
            },
            {
                'name': 'Professional Yoga Mat',
                'description': 'Extra thick yoga mat with alignment lines and carrying strap.',
                'price': Decimal('29.99'),
                'stock': 75,
                'category': 'Sports',
                'additional_details': '6mm thickness\nNon-slip surface\nIncludes carrying strap'
            },
            {
                'name': 'Luxury Skincare Set',
                'description': 'Complete skincare set with cleanser, toner, and moisturizer.',
                'price': Decimal('69.99'),
                'stock': 60,
                'category': 'Beauty',
                'additional_details': '3-piece set\nSuitable for all skin types\nParaben-free'
            },
            {
                'name': 'Educational Building Blocks',
                'description': 'STEM learning building blocks set for children.',
                'price': Decimal('39.99'),
                'stock': 45,
                'category': 'Toys',
                'additional_details': '100 pieces\nAges 6+\nIncludes instruction manual'
            },
            {
                'name': 'Garden Tool Set',
                'description': 'Complete set of essential gardening tools.',
                'price': Decimal('59.99'),
                'stock': 35,
                'category': 'Garden',
                'additional_details': '8-piece set\nErgonomic handles\nStorage bag included'
            },
            {
                'name': 'Wireless Charging Pad',
                'description': 'Fast wireless charging pad compatible with all Qi-enabled devices.',
                'price': Decimal('34.99'),
                'stock': 80,
                'category': 'Electronics',
                'additional_details': '15W fast charging\nLED indicator\nOvercharge protection'
            },
            {
                'name': 'Designer Sunglasses',
                'description': 'UV protection sunglasses with polarized lenses.',
                'price': Decimal('89.99'),
                'stock': 55,
                'category': 'Fashion',
                'additional_details': '100% UV protection\nPolarized lenses\nIncludes case'
            },
            {
                'name': 'Smart Home Speaker',
                'description': 'Voice-controlled smart speaker with premium sound quality.',
                'price': Decimal('129.99'),
                'stock': 40,
                'category': 'Electronics',
                'additional_details': 'Voice assistant\n360° sound\nMulti-room audio'
            },
            {
                'name': 'Professional Hair Dryer',
                'description': 'Ionic hair dryer with multiple heat settings.',
                'price': Decimal('79.99'),
                'stock': 65,
                'category': 'Beauty',
                'additional_details': '3 heat settings\nIonic technology\nIncludes diffuser'
            },
            {
                'name': 'Fitness Tracker',
                'description': 'Advanced fitness tracker with heart rate monitoring.',
                'price': Decimal('89.99'),
                'stock': 70,
                'category': 'Sports',
                'additional_details': 'Heart rate monitor\nSleep tracking\nWater resistant'
            },
            {
                'name': 'Indoor Plant Collection',
                'description': 'Set of 3 low-maintenance indoor plants.',
                'price': Decimal('49.99'),
                'stock': 30,
                'category': 'Garden',
                'additional_details': '3 plants\nIncludes pots\nCare instructions'
            }
        ]
        
        # Create products
        for product_data in products_data:
            category = created_categories[product_data['category']]
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'category': category,
                    'seller': admin_user,
                    'additional_details': product_data['additional_details'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added more sample products')) 