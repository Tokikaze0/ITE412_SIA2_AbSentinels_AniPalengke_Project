from django.core.management.base import BaseCommand
from core.models import Article

class Command(BaseCommand):
    help = 'Seeds the database with initial articles'

    def handle(self, *args, **kwargs):
        if Article.objects.count() > 0:
            self.stdout.write(self.style.SUCCESS('Articles already exist. Skipping seed.'))
            return

        articles = [
            {
                'title': 'Sustainable Farming 101',
                'summary': 'Learn the basics of sustainable agriculture and how it benefits the environment.',
                'content': 'Sustainable farming is about meeting the needs of the present without compromising the ability of future generations to meet their own needs. It involves methods that protect the environment, public health, human communities, and animal welfare. Key practices include crop rotation, cover cropping, and reduced tillage.',
                'category': 'Farming Tips'
            },
            {
                'title': 'Understanding Crop Rotation',
                'summary': 'Why rotating your crops is essential for soil health and pest management.',
                'content': 'Crop rotation is the practice of planting different crops sequentially on the same plot of land to improve soil health, optimize nutrients in the soil, and combat pest and weed pressure. For example, say a farmer has planted a field of corn. When the corn harvest is finished, he might plant beans, since corn consumes a lot of nitrogen and beans return nitrogen to the soil.',
                'category': 'Soil Health'
            },
            {
                'title': 'Market Trends for 2025',
                'summary': 'What to expect in the agricultural market this year.',
                'content': 'The agricultural market in 2025 is expected to see a rise in demand for organic and locally sourced produce. Technology adoption, such as precision farming and AI-driven analytics, will continue to grow, helping farmers optimize yields and reduce waste. Consumers are also becoming more conscious of the carbon footprint of their food.',
                'category': 'Market News'
            },
            {
                'title': 'Pest Control Without Chemicals',
                'summary': 'Natural ways to keep pests away from your crops.',
                'content': 'Integrated Pest Management (IPM) is an ecosystem-based strategy that focuses on long-term prevention of pests or their damage through a combination of techniques such as biological control, habitat manipulation, modification of cultural practices, and use of resistant varieties. Pesticides are used only after monitoring indicates they are needed according to established guidelines, and treatments are made with the goal of removing only the target organism.',
                'category': 'Pest Control'
            }
        ]

        for data in articles:
            Article.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"Created article: {data['title']}"))
