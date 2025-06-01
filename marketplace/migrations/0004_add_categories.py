from django.db import migrations

def add_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    categories = [
        {
            'name': 'Handmade Jewelry',
            'description': 'Unique and beautiful handmade jewelry pieces including necklaces, bracelets, earrings, and rings.'
        },
        {
            'name': 'Home Decor',
            'description': 'Artisanal home decoration items including wall art, decorative pieces, and handmade furniture.'
        },
        {
            'name': 'Textiles & Fabrics',
            'description': 'Handcrafted textiles including quilts, blankets, pillows, and fabric accessories.'
        },
        {
            'name': 'Art & Paintings',
            'description': 'Original artwork, paintings, prints, and other artistic creations.'
        },
        {
            'name': 'Candles & Soaps',
            'description': 'Handmade candles, soaps, and other bath and body products.'
        },
        {
            'name': 'Wood Crafts',
            'description': 'Handcrafted wooden items including furniture, decorative pieces, and kitchenware.'
        },
        {
            'name': 'Ceramics & Pottery',
            'description': 'Handmade ceramic and pottery items including vases, mugs, plates, and decorative pieces.'
        }
    ]
    
    for category_data in categories:
        Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data['description']}
        )

def remove_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ] 