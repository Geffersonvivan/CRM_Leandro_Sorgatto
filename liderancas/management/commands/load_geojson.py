"""
Baixa GeoJSON dos municipios de SC do IBGE e agrupa por regiao,
salvando o geometry de cada cidade e o geometry agregado de cada regiao.
"""
import gzip
import json
import urllib.request
from django.core.management.base import BaseCommand
from liderancas.models import Regiao, Cidade


class Command(BaseCommand):
    help = 'Baixa GeoJSON de SC do IBGE e salva nos models'

    def _rewind_geometry(self, geometry):
        """Reverte winding order dos poligonos para compatibilidade com D3.
        D3 usa convencao oposta ao RFC 7946: exterior rings devem ser horarios."""
        def reverse_ring(ring):
            return list(reversed(ring))

        geo_type = geometry['type']
        coords = geometry['coordinates']

        if geo_type == 'Polygon':
            new_coords = [reverse_ring(ring) for ring in coords]
            return {'type': 'Polygon', 'coordinates': new_coords}
        elif geo_type == 'MultiPolygon':
            new_coords = []
            for polygon in coords:
                new_coords.append([reverse_ring(ring) for ring in polygon])
            return {'type': 'MultiPolygon', 'coordinates': new_coords}
        return geometry

    def handle(self, *args, **options):
        url = 'https://servicodados.ibge.gov.br/api/v3/malhas/estados/42?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio'
        self.stdout.write('Baixando malha municipal de SC do IBGE...')

        try:
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
            })
            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read()
                try:
                    data = raw.decode('utf-8')
                except UnicodeDecodeError:
                    data = gzip.decompress(raw).decode('utf-8')
                geojson = json.loads(data)
        except Exception as e:
            self.stderr.write(f'Erro ao acessar IBGE: {e}')
            return

        features = geojson.get('features', [])
        self.stdout.write(f'{len(features)} municipios encontrados no GeoJSON')

        cities_updated = 0
        for feature in features:
            codarea = feature.get('properties', {}).get('codarea', '')
            if not codarea:
                continue
            try:
                city = Cidade.objects.get(codigo_ibge=codarea)
                city.geojson = self._rewind_geometry(feature['geometry'])
                city.save(update_fields=['geojson'])
                cities_updated += 1
            except Cidade.DoesNotExist:
                pass

        self.stdout.write(f'{cities_updated} cidades atualizadas com GeoJSON')

        regions_updated = 0
        for region in Regiao.objects.all():
            cities_with_geo = region.cidades.exclude(geojson__isnull=True)
            if not cities_with_geo.exists():
                continue

            polygons = []
            for city in cities_with_geo:
                geo = city.geojson
                if geo['type'] == 'Polygon':
                    polygons.append(geo['coordinates'])
                elif geo['type'] == 'MultiPolygon':
                    polygons.extend(geo['coordinates'])

            region.geojson = {
                'type': 'MultiPolygon',
                'coordinates': polygons,
            }
            region.save(update_fields=['geojson'])
            regions_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'{regions_updated} regioes atualizadas com GeoJSON agregado'
        ))
