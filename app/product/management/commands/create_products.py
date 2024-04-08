import os
import uuid

from django.core.management.base import BaseCommand
from random import randint, choice
from faker import Faker

from account.models import User
from account import RoleType
from product.models import Product, Image, Category, Type, Convenience, Comment
from helpers.logger import log_exception

from io import BytesIO
import cairosvg
from django.core.files.base import ContentFile

fake = Faker()
PRODUCT_COUNT = 500


class Command(BaseCommand):
    help = f'Create {PRODUCT_COUNT} products'
    images = (
        '/code/product/management/images/houses/img1.jpg',
        '/code/product/management/images/houses/img2.jpg',
        '/code/product/management/images/houses/img3.jpg',
        '/code/product/management/images/houses/img4.jpg',
        '/code/product/management/images/houses/img5.jpg',
        '/code/product/management/images/houses/img6.webp',
        '/code/product/management/images/houses/img7.webp',
        '/code/product/management/images/houses/img8.webp',
        '/code/product/management/images/houses/img9.jpeg',
        '/code/product/management/images/houses/img10.jpeg',
        '/code/product/management/images/houses/img11.jpeg',
        '/code/product/management/images/houses/img12.jpeg',
    )
    categories = {
        '/code/product/management/images/categories/башни.svg': 'Башни',
        '/code/product/management/images/categories/большие кухни.svg': 'Большие кухни',
        '/code/product/management/images/categories/вау.svg': 'Вау',
        '/code/product/management/images/categories/вершины мира.svg': 'Вершины мира',
        '/code/product/management/images/categories/supermarket.svg': 'Магазин',
        '/code/product/management/images/categories/виноградники.svg': 'Виноградники',
        '/code/product/management/images/categories/гольф.svg': 'Гольф',
        '/code/product/management/images/categories/популярные.svg': 'Популярные',
        '/code/product/management/images/categories/кумыс.svg': 'Кумыс',
        '/code/product/management/images/categories/города мечты.svg': 'Города мечты',
        '/code/product/management/images/categories/гостиницы.svg': 'Гостиница',
        '/code/product/management/images/categories/dices.svg': 'Казино',
        '/code/product/management/images/categories/дер дома.svg': 'Деревянные дома',
        '/code/product/management/images/categories/дома шалаши.svg': 'Дома шалаши',
        '/code/product/management/images/categories/загородные дома.svg': 'Загородные дома',
        '/code/product/management/images/categories/pub.svg': 'Бар',
        '/code/product/management/images/categories/у озера.svg': 'Дом у озера',
        '/code/product/management/images/categories/купольный дом.svg': 'Купольные дома',
        '/code/product/management/images/categories/skis.svg': 'Горнолыжная база',
        '/code/product/management/images/categories/микродома.svg': 'Микродома',
        '/code/product/management/images/categories/новинки.svg': 'Новинки',
        '/code/product/management/images/categories/лыжня.svg': 'Рядом с лыжней базы',
        '/code/product/management/images/categories/юрта.svg': 'Юрта',
        '/code/product/management/images/categories/restaurant.svg': 'Ресторан',
        '/code/product/management/images/categories/отд комнаты.svg': 'Отдельные комнаты',
        '/code/product/management/images/categories/кемпинг.svg': 'Кемпинг',
        '/code/product/management/images/categories/особняки.svg': 'Особняк',
        '/code/product/management/images/categories/bbq.svg': 'BBQ зона',
        '/code/product/management/images/categories/little-home.svg': 'Коттедж',
        '/code/product/management/images/categories/отличные виды.svg': 'Отличный вид',
        '/code/product/management/images/categories/отопление.svg': 'Отопление',
        '/code/product/management/images/categories/pharmacy.svg': 'Аптека',
        '/code/product/management/images/categories/игры.svg': 'Игры',
        '/code/product/management/images/categories/пейзаж.svg': 'Пейзаж',
        '/code/product/management/images/categories/пещеры.svg': 'Пещеры',
        '/code/product/management/images/categories/рядом пляж.svg': 'Пляж',
        '/code/product/management/images/categories/heart.svg': 'Санаторий',
        '/code/product/management/images/categories/рабочая зона.svg': 'Рабочая зона',
        '/code/product/management/images/categories/намазхана.svg': 'Намазхана',
        '/code/product/management/images/categories/сауна.svg': 'Сауна',
        '/code/product/management/images/categories/супербассейны.svg': 'Супербассейны',
        '/code/product/management/images/categories/люкс.svg': 'Luxe',
    }
    conveniences = {
        '/code/product/management/images/convenience/wifi.svg': 'Wifi',
        '/code/product/management/images/convenience/vanna.svg': 'Ванная',
        '/code/product/management/images/convenience/shampon.svg': 'Шампунь',
        '/code/product/management/images/convenience/fen.svg': 'Фен',
        '/code/product/management/images/convenience/kondor.svg': 'Кондиционер',
        '/code/product/management/images/convenience/pred_perv_neb.svg': 'Предметы первой необходимости',
        '/code/product/management/images/convenience/post_bel.svg': 'Постельное белье',
        '/code/product/management/images/convenience/podushka.svg': 'Дополнительные подушки и одеяла',
        '/code/product/management/images/convenience/grderob.svg': 'Место для хранения одежды',
        '/code/product/management/images/convenience/tv.svg': 'Телевизор',
        '/code/product/management/images/convenience/kamin.svg': 'Камин',
        '/code/product/management/images/convenience/ognetush.svg': 'Огнетушитель',
        '/code/product/management/images/convenience/aptechka.svg': 'Аптечка',
        '/code/product/management/images/convenience/kuh.svg': 'Кухня',
        '/code/product/management/images/convenience/posuda.svg': 'Посуда и столовые приборы',
        '/code/product/management/images/convenience/elektro_plita.svg': 'Электроплита',
        '/code/product/management/images/convenience/koffe_varka.svg': 'Кофеварка',
        '/code/product/management/images/convenience/obed_stol.svg': 'Обеденный стол',
        '/code/product/management/images/convenience/dvorik_balkon.svg': 'Дворик (патио) или балкон с частным доступом',
        '/code/product/management/images/convenience/krovat.svg': 'Kроватка',
        '/code/product/management/images/convenience/ulich_meb.svg': 'Уличная мебель',
        '/code/product/management/images/convenience/bbk.svg': 'Зона барбекю',
        '/code/product/management/images/convenience/parkovka.svg': 'Бесплатная парковка на территории',
        '/code/product/management/images/convenience/bassein.svg': 'Бассейн: Частный доступ',
        '/code/product/management/images/convenience/hos_vstre.svg': 'Хозяин встретит вас лично',
        '/code/product/management/images/convenience/stir_mach.svg': 'Стиральная машина',
        '/code/product/management/images/convenience/datchik_dim.svg': 'Датчик дыма',
        '/code/product/management/images/convenience/datch_ugar_dim.svg': 'Датчик угарного газа',
        '/code/product/management/images/convenience/camera.svg': 'Камеры видеонаблюдения в жилье',
        '/code/product/management/images/convenience/utug.svg': 'Утюг',
        '/code/product/management/images/convenience/gidro_mass.svg': 'Гидромассажная ванна',
        '/code/product/management/images/convenience/gor_voda.svg': 'Горячая вода',
        '/code/product/management/images/convenience/gas_petch.svg': 'Газавая печка',
        '/code/product/management/images/convenience/dush_ul.svg': 'Душ на улице',
        '/code/product/management/images/convenience/zad_dvor.svg': 'Задний двор',
        '/code/product/management/images/convenience/mikrovol.svg': 'Микроволновка',
        '/code/product/management/images/convenience/otdel_vhod.svg': 'Отдельный вход',
        '/code/product/management/images/convenience/lezhaki.svg': 'Лежаки',
        '/code/product/management/images/convenience/plech.svg': 'Плечики',
        '/code/product/management/images/convenience/posuda_moi_mach.svg': 'Посудомоечная машина',
        '/code/product/management/images/convenience/protiv.svg': 'Вкусно поесть',
        '/code/product/management/images/convenience/work_area.svg': 'Рабочая зона',
        '/code/product/management/images/convenience/stol_korm.svg': 'Стульчик для кормления',
        '/code/product/management/images/convenience/sushul_odezh.svg': 'Сушилка для одежды',
        '/code/product/management/images/convenience/toster.svg': 'Тостер',
        '/code/product/management/images/convenience/holod.svg': 'Холодильник',
        '/code/product/management/images/convenience/center_otop.svg': 'Центр отопление',
        '/code/product/management/images/convenience/chainik.svg': 'Чайник',
    }
    types = (
        'Панельные дома',
        'Блочные дома',
        'Монолитные дома',
        'Каменные дома',
        'Бетонные дома',
        'Металлические дома',
        'Соломенные дома',
        'Глинобитные дома',
        'Шале',
        'Фахверк',
        'Дома из бамбука',
        'Дома из стекла',
        'Мобильные дома',
        'Хайтек дома',
        'Современные дома',
    )
    coordinates = [
        {
            'lat': '42.09911578535362',
            'lng': '69.99540527229699'
        },
        {
            'lat': '42.097840435792435',
            'lng': '69.99062712438808'
        },
        {
            'lat': '42.0967174',
            'lng': '69.994004'
        },
        {
            'lat': '42.0938863',
            'lng': '69.998852'
        },
        {
            'lat': '42.0936579',
            'lng': '70.0003002'
        },
        {
            'lat': '42.0936579',
            'lng': '70.0003002'
        },
        {
            'lat': '42.0926236',
            'lng': '70.0014527'
        },
        {
            'lat': '42.0913823',
            'lng': '70.0095129'
        },
        {
            'lat': '42.0905091',
            'lng': '70.0091327'
        },
        {
            'lat': '42.0998436',
            'lng': '70.0023506'
        },
        {
            'lat': '2.0994875',
            'lng': '69.9996043'
        },
        {
            'lat': '42.0981561',
            'lng': '69.9888781'
        },
        {
            'lat': '42.0915347',
            'lng': '69.9809232'
        },
        {
            'lat': '42.0879649',
            'lng': '69.9755303'
        },
        {
            'lat': '42.0879649',
            'lng': '69.9755303'
        }
    ]

    def handle(self, *args, **kwargs):
        try:
            print('Starting create products...')

            for icon_path, category_name in self.categories.items():
                User.objects.create_user(fake.email(), fake.password(6), role=RoleType.MANAGER,
                                         last_name=fake.last_name(), first_name=fake.first_name(),
                                         middle_name=fake.word(), date_of_birth="1970-01-01",
                                         phone_number=fake.phone_number(), is_active=True)

                print(f'Create category {category_name}')

                png_data = cairosvg.svg2png(url=icon_path)
                png_io = BytesIO(png_data)
                random_name = f'{uuid.uuid4()}.jpeg'
                cate = Category.objects.create(name=category_name)
                cate.icon.save(random_name, ContentFile(png_io.getvalue()), save=True)

            for icon_path, convenience_name in self.conveniences.items():
                conv = Convenience.objects.create(name=convenience_name)
                random_name = f'{uuid.uuid4()}.jpeg'
                png_data = cairosvg.svg2png(url=icon_path)
                png_io = BytesIO(png_data)
                conv.icon.save(random_name, ContentFile(png_io.getvalue()), save=True)

                print(f'Create conveniences {convenience_name}')

            for h_type in self.types:
                Type.objects.create(name=h_type)

            for _ in range(PRODUCT_COUNT):
                coords = choice(self.coordinates)
                data = {
                    'name': fake.name(),
                    'price_per_night': randint(100, 1000),
                    'price_per_week': randint(1000, 10000),
                    'price_per_month': randint(1000, 50000),
                    'owner_id': randint(1, 40),
                    'rooms_qty': randint(1, 12),
                    'guest_qty': randint(1, 30),
                    'guests_with_babies': choice((True, False)),
                    'guests_with_pets': choice((True, False)),
                    'bed_qty': randint(1, 10),
                    'bedroom_qty': randint(1, 10),
                    'toilet_qty': randint(1, 10),
                    'bath_qty': randint(1, 10),
                    'description': fake.paragraph(nb_sentences=3),
                    'city': fake.city(),
                    'address': fake.address(),
                    'type_id': randint(1, len(self.types)),
                    'lng': coords.get('lng', 0),
                    'lat': coords.get('lat', 0),
                    'is_active': True,
                    'like_count': randint(5, 100),
                    'rating': randint(1, 5),
                    'best_product': choice((True, False)),
                    'promotion': choice((True, False)),
                }
                product = Product.objects.create(**data)
                product.category.set([randint(1, len(self.categories))
                                      for _ in range(randint(1, len(self.categories)))])
                product.convenience.set([randint(1, len(self.conveniences))
                                         for _ in range(randint(1, len(self.conveniences)))])

                print(f'Product {_} created')

                for _ in range(15):
                    image_url = choice(self.images)
                    is_label = True if _ == 1 else False
                    image = Image(product=product, is_label=is_label)
                    image.original.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.thumbnail.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.save()

                for _ in range(8):
                    content = f"Comment {_}"
                    user = User.objects.order_by('?').first()
                    Comment.objects.create(content=content, is_active=True, user=user, product=product)

        except Exception as e:
            log_exception(e)
            return
