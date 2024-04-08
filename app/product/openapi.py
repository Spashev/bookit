from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

category = openapi.Parameter('category', openapi.IN_QUERY, description="Category", type=openapi.TYPE_INTEGER)
start_date = openapi.Parameter('start_date', openapi.IN_QUERY, description="Date start", type=openapi.FORMAT_DATE)
end_date = openapi.Parameter('end_date', openapi.IN_QUERY, description="Date end", type=openapi.FORMAT_DATE)
guest_count = openapi.Parameter(
    'guest_count', openapi.IN_QUERY, description="Guests total counts", type=openapi.TYPE_INTEGER
)
guests_with_babies = openapi.Parameter(
    'guests_with_babies', openapi.IN_QUERY, description="Guests with babies", type=openapi.TYPE_BOOLEAN
)
guests_with_pets = openapi.Parameter(
    'guests_with_pets', openapi.IN_QUERY, description="Guests with pets", type=openapi.TYPE_BOOLEAN
)
min_price = openapi.Parameter('min_price', openapi.IN_QUERY, description="Min price", type=openapi.TYPE_INTEGER)
max_price = openapi.Parameter('max_price', openapi.IN_QUERY, description="Max price", type=openapi.TYPE_INTEGER)
rooms_qty = openapi.Parameter('rooms_qty', openapi.IN_QUERY, description="Rooms total counts, limit 8+",
                              type=openapi.TYPE_INTEGER)
house_name = openapi.Parameter('house_name', openapi.IN_QUERY, description="House name", type=openapi.TYPE_STRING)
house_type = openapi.Parameter('house_type', openapi.IN_QUERY, description="House type", type=openapi.TYPE_STRING)
bath_qty = openapi.Parameter(
    'bath_qty', openapi.IN_QUERY, description="Bath total counts, limit 4+", type=openapi.TYPE_INTEGER
)
bed_qty = openapi.Parameter(
    'bed_qty', openapi.IN_QUERY, description="Bed total counts, limit 6+", type=openapi.TYPE_INTEGER
)
bedroom_qty = openapi.Parameter(
    'bedroom_qty', openapi.IN_QUERY, description="Bedroom total counts, limit 6+", type=openapi.TYPE_INTEGER
)
limit = openapi.Parameter('limit', openapi.IN_QUERY, description="Limit", type=openapi.TYPE_INTEGER)
offset = openapi.Parameter('offset', openapi.IN_QUERY, description="Offset", type=openapi.TYPE_INTEGER)
active = openapi.Parameter('active', openapi.IN_QUERY, description="Product active", type=openapi.TYPE_BOOLEAN)

manual_parameters = [
    house_name, min_price, max_price, start_date, end_date, guest_count, guests_with_babies, guests_with_pets,
    rooms_qty, bed_qty, bath_qty, bedroom_qty, category, house_type, limit, offset
]
