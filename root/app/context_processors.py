

from .models import Region

def safari_index(request):
    return {'regions': Region.objects.prefetch_related('subregions__safaris').all()}

