from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Category, Product
from decimal import Decimal
import os

class Command(BaseCommand):
    help = 'Adds sample products to the database'

    def handle(self, *args, **kwargs):
        # Get or create admin user
        admin_user = User.objects.get(username='ManojV')
        
        # Create categories
        categories = {
            'Handmade Jewelry': 'Beautiful handcrafted jewelry pieces',
            'Home Decor': 'Unique decorative items for your home',
            'Art & Paintings': 'Original artwork and paintings',
            'Textiles': 'Handwoven and handcrafted textile items',
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
                'name': 'Silver Pendant Necklace',
                'description': 'Handcrafted silver pendant necklace with intricate design. Perfect for special occasions.',
                'price': Decimal('49.99'),
                'stock': 10,
                'category': 'Handmade Jewelry',
                'additional_details': 'Made with 925 sterling silver\nLength: 18 inches\nIncludes gift box'
            },
            {
                'name': 'Ceramic Vase Set',
                'description': 'Set of 3 hand-painted ceramic vases in complementary colors. Each piece is unique.',
                'price': Decimal('89.99'),
                'stock': 5,
                'category': 'Home Decor',
                'additional_details': 'Dimensions: Small (6"), Medium (8"), Large (10")\nHand wash only'
            },
            {
                'name': 'Abstract Canvas Painting',
                'description': 'Original abstract painting on canvas using acrylic paints. Adds a modern touch to any room.',
                'price': Decimal('299.99'),
                'stock': 1,
                'category': 'Art & Paintings',
                'additional_details': 'Size: 24" x 36"\nComes with hanging hardware\nSigned by the artist'
            },
            {
                'name': 'Handwoven Cotton Scarf',
                'description': 'Beautiful handwoven cotton scarf with traditional patterns. Lightweight and versatile.',
                'price': Decimal('39.99'),
                'stock': 15,
                'category': 'Textiles',
                'additional_details': 'Dimensions: 70" x 24"\n100% organic cotton\nMachine washable'
            },
            {
                'name': 'Gemstone Earrings',
                'description': 'Handmade earrings featuring natural gemstones and sterling silver. Each pair is unique.',
                'price': Decimal('34.99'),
                'stock': 8,
                'category': 'Handmade Jewelry',
                'additional_details': 'Materials: Sterling silver, natural gemstones\nLength: 1.5 inches'
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
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample products')) 