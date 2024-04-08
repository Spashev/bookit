from datetime import datetime, timedelta
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q, Exists, OuterRef, Prefetch, Case, When, Value, BooleanField

from product.models import Product, Booking, Image, Category, Comment, Favorites, Type, Convenience
from helpers.serializers import UserSerializer, ImageSerializer as ProductImageSerializer
from helpers.constants import ROOM_LIMIT, BED_LIMIT, BATH_LIMIT, BEDROOM_LIMIT


def like_or_dislike(obj, user) -> dict:
    likes = user.likes.filter(product=obj)
    if likes:
        likes.first().delete()
        message = {'message': 'Product like removed.'}
    else:
        obj.like.create(user=user)
        message = {'message': 'Product liked.'}

    return message


def save_image(product, data) -> tuple:
    uploaded_files = data.pop('uploaded_files[]')
    for file in uploaded_files:
        if (
                file.content_type != 'image/png' and file.content_type != 'image/jpeg'
                and file.content_type != 'image/jpg' and file.content_type != 'image/gif'
                and file.content_type != 'image/webp'
        ):
            return False, {'uploaded_files': 'Неверный формат файла'}

    for file in uploaded_files:
        Image.objects.create(product=product, original=file, thumbnail=file)

    return True, {'message': 'Images saved success'}


def get_product_by_id_user_id(product_id, user_id=None):
    product = Product.with_related
    if user_id:
        product = product.annotate(
            is_favorite=Exists(
                Favorites.objects.filter(user_id=user_id, product_id=product_id)
            )
        )

    return product.annotate(
        is_new=Case(
            When(created_at__gte=datetime.now() - timedelta(days=7), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    ).get(pk=product_id)


def get_product_queryset(q, user_id):
    queryset = Product.active_related.filter(q)
    if user_id:
        queryset = queryset.annotate(
            is_favorite=Exists(
                Favorites.objects.filter(user_id=user_id, product_id=OuterRef('id'))
            )
        )

    return queryset.annotate(
        is_new=Case(
            When(created_at__gte=datetime.now() - timedelta(days=7), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    ).order_by('?')


def paginate_queryset(queryset, request):
    offset = request.GET.get('offset', None)
    paginator = LimitOffsetPagination()
    paginator.page_size = offset if offset else 25

    return paginator, paginator.paginate_queryset(queryset, request)


def get_user_products(user):
    return user.products.prefetch_related('owner', 'images').annotate(
        is_new=Case(
            When(created_at__gte=datetime.now() - timedelta(days=7), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )


def get_favorite_products(user):
    return Product.active_related.prefetch_related(
        Prefetch('favorites', queryset=Favorites.objects.filter(user=user)),
        'owner',
        'images'
    ).annotate(
        is_new=Case(
            When(created_at__gte=datetime.now() - timedelta(days=7), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).filter(favorites__user=user)


def get_favorite_products_data(products):
    return [
        {
            'id': product.id,
            'name': product.name,
            'price_per_night': product.price_per_night,
            'owner': UserSerializer(product.owner).data,
            'city': product.city,
            'address': product.address,
            'images': product.images,
            'is_favorite': True,
            'rating': product.rating,
            'like_count': product.like_count,
            'is_new': product.is_new,
            'best_product': product.best_product,
        }
        for product in products
    ]


def get_product_bookings(product, request=None):
    start_date_param = request.GET.get('start_date', None) if request else None
    end_date_param = request.GET.get('end_date', None) if request else None

    current_date = datetime.now()
    last_day_of_month = current_date.replace(day=1, month=current_date.month + 2) - timedelta(days=1)

    start_date_param = datetime.now() if start_date_param is None else start_date_param
    end_date_param = last_day_of_month if end_date_param is None else end_date_param

    start_date = start_date_param
    end_date = end_date_param

    return product.booking.filter(
        Q(start_date__range=(start_date, end_date)) |
        Q(end_date__range=(start_date, end_date)) |
        (Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
    )


def sort_products_images(images):
    return sorted(images, key=lambda x: not x['is_label'])


def get_query_filter(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    guest_count = request.GET.get('guest_count', 1)
    guests_with_pets = request.GET.get('guests_with_pets', False)
    guests_with_babies = request.GET.get('guests_with_babies', False)
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    rooms_qty = request.GET.get('rooms_qty', None)
    bed_qty = request.GET.get('bed_qty', None)
    bath_qty = request.GET.get('bath_qty', None)
    bedroom_qty = request.GET.get('bedroom_qty', None)
    category = request.GET.get('category', None)
    house_type = request.GET.get('house_type', None)
    house_name = request.GET.get('house_name', None)

    q = Q()

    if house_name is not None:
        q &= Q(name__icontains=house_name)

    if min_price is not None:
        q &= Q(price_per_night__gte=min_price)

    if max_price is not None:
        q &= Q(price_per_night__lte=max_price)

    if start_date is not None and end_date is not None:
        q &= ~Q(booking__end_date__range=(start_date, end_date))

    if guest_count is not None:
        q &= Q(guest_qty__gte=guest_count)

    if guests_with_pets and guests_with_pets != 'false':
        q &= Q(guests_with_pets=True)

    if guests_with_babies and guests_with_babies != 'false':
        q &= Q(guests_with_babies=True)

    if rooms_qty is not None and int(rooms_qty) <= ROOM_LIMIT:
        q &= Q(rooms_qty__gte=rooms_qty)

    if bed_qty is not None and int(bed_qty) <= BED_LIMIT:
        q &= Q(bed_qty__gte=bed_qty)

    if bath_qty is not None and int(bath_qty) <= BATH_LIMIT:
        q &= Q(bath_qty__gte=bath_qty)

    if bedroom_qty is not None and int(bedroom_qty) <= BEDROOM_LIMIT:
        q &= Q(bedroom_qty__gte=bedroom_qty)

    if category is not None:
        q &= Q(category__pk=category)

    if house_type is not None:
        q &= Q(type__pk__in=house_type.split(","))

    return q
