"""
Carrega todas as cidades de Santa Catarina do IBGE API
e associa a regiao (associacao de municipios) correspondente.
Mapeamento oficial: SAS/SC - Lista de Municipios por Associacao FECAM.
"""
import gzip
import json
import urllib.request
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from liderancas.models import Regiao, Cidade

# Mapeamento de municipios para associacoes (IBGE code -> region slug)
CITY_REGION_MAP = {
    # AMAI (14 municipios)
    "4200101": "amai", "4202537": "amai", "4205175": "amai", "4205308": "amai",
    "4207684": "amai", "4209458": "amai", "4210555": "amai", "4211850": "amai",
    "4212270": "amai", "4213401": "amai", "4216107": "amai", "4219101": "amai",
    "4219507": "amai", "4219705": "amai",
    # AMARP (15 municipios)
    "4201604": "amarp", "4203006": "amarp", "4203154": "amarp", "4205506": "amarp",
    "4206751": "amarp", "4207577": "amarp", "4209706": "amarp", "4210050": "amarp",
    "4210704": "amarp", "4213005": "amarp", "4214409": "amarp", "4215406": "amarp",
    "4217907": "amarp", "4218251": "amarp", "4219309": "amarp",
    # AMAUC (14 municipios)
    "4200754": "amauc", "4201273": "amauc", "4204301": "amauc", "4207601": "amauc",
    "4207700": "amauc", "4207809": "amauc", "4208005": "amauc", "4208609": "amauc",
    "4209854": "amauc", "4212601": "amauc", "4213104": "amauc", "4213906": "amauc",
    "4217501": "amauc", "4219606": "amauc",
    # AMAVI (28 municipios)
    "4200200": "amavi", "4200309": "amavi", "4201802": "amavi", "4201901": "amavi",
    "4202859": "amavi", "4204194": "amavi", "4205100": "amavi", "4206900": "amavi",
    "4207403": "amavi", "4208500": "amavi", "4209151": "amavi", "4209508": "amavi",
    "4209904": "amavi", "4210852": "amavi", "4212700": "amavi", "4213708": "amavi",
    "4214003": "amavi", "4214102": "amavi", "4214508": "amavi", "4214607": "amavi",
    "4214805": "amavi", "4215307": "amavi", "4215679": "amavi", "4217808": "amavi",
    "4218608": "amavi", "4219200": "amavi", "4219358": "amavi", "4219408": "amavi",
    # AMEOSC (19 municipios)
    "4200804": "ameosc", "4202081": "ameosc", "4202099": "ameosc", "4202156": "ameosc",
    "4204905": "ameosc", "4205001": "ameosc", "4206405": "ameosc", "4206603": "ameosc",
    "4207650": "ameosc", "4208401": "ameosc", "4211009": "ameosc", "4212007": "ameosc",
    "4212239": "ameosc", "4214151": "ameosc", "4215554": "ameosc", "4216255": "ameosc",
    "4216701": "ameosc", "4217204": "ameosc", "4218756": "ameosc",
    # AMERIOS (17 municipios)
    "4202578": "amerios", "4203105": "amerios", "4203501": "amerios", "4204707": "amerios",
    "4204756": "amerios", "4205357": "amerios", "4207759": "amerios", "4210506": "amerios",
    "4210902": "amerios", "4212106": "amerios", "4215075": "amerios", "4215208": "amerios",
    "4215356": "amerios", "4215687": "amerios", "4217154": "amerios", "4217303": "amerios",
    "4217956": "amerios",
    # AMESC (15 municipios)
    "4201406": "amesc", "4201950": "amesc", "4202073": "amesc", "4205191": "amesc",
    "4208708": "amesc", "4210407": "amesc", "4210803": "amesc", "4211256": "amesc",
    "4212254": "amesc", "4213807": "amesc", "4215653": "amesc", "4216404": "amesc",
    "4217709": "amesc", "4218103": "amesc", "4218806": "amesc",
    # AMFRI (11 municipios)
    "4202008": "amfri", "4202453": "amfri", "4203204": "amfri", "4207106": "amfri",
    "4208203": "amfri", "4208302": "amfri", "4210001": "amfri", "4211306": "amfri",
    "4212502": "amfri", "4212809": "amfri", "4213500": "amfri",
    # AMMOC (12 municipios)
    "4200408": "ammoc", "4203907": "ammoc", "4204004": "ammoc", "4205209": "ammoc",
    "4206702": "ammoc", "4206801": "ammoc", "4209003": "ammoc", "4209201": "ammoc",
    "4210035": "ammoc", "4211801": "ammoc", "4218509": "ammoc", "4219176": "ammoc",
    # AMNOROESTE (8 municipios)
    "4204459": "amnoroeste", "4205605": "amnoroeste", "4207858": "amnoroeste",
    "4209177": "amnoroeste", "4211652": "amnoroeste", "4214201": "amnoroeste",
    "4215752": "amnoroeste", "4216909": "amnoroeste",
    # AMOSC (20 municipios)
    "4200507": "amosc", "4200556": "amosc", "4201653": "amosc", "4204103": "amosc",
    "4204202": "amosc", "4204350": "amosc", "4204400": "amosc", "4205431": "amosc",
    "4206652": "amosc", "4208955": "amosc", "4211405": "amosc", "4211454": "amosc",
    "4211876": "amosc", "4212908": "amosc", "4213153": "amosc", "4215695": "amosc",
    "4216008": "amosc", "4217550": "amosc", "4217758": "amosc", "4218855": "amosc",
    # AMPLANORTE (10 municipios)
    "4202131": "amplanorte", "4203808": "amplanorte", "4207908": "amplanorte",
    "4208104": "amplanorte", "4210100": "amplanorte", "4210308": "amplanorte",
    "4211108": "amplanorte", "4212205": "amplanorte", "4213609": "amplanorte",
    "4218301": "amplanorte",
    # AMPLASC (7 municipios)
    "4200051": "amplasc", "4202875": "amplasc", "4203600": "amplasc", "4204152": "amplasc",
    "4211058": "amplasc", "4219150": "amplasc", "4219853": "amplasc",
    # AMREC (12 municipios)
    "4204251": "amrec", "4204608": "amrec", "4205456": "amrec", "4207007": "amrec",
    "4209607": "amrec", "4211207": "amrec", "4211603": "amrec", "4211702": "amrec",
    "4217600": "amrec", "4218350": "amrec", "4219002": "amrec", "4220000": "amrec",
    # AMUNESC (9 municipios)
    "4201307": "amunesc", "4202057": "amunesc", "4203303": "amunesc", "4205803": "amunesc",
    "4208450": "amunesc", "4209102": "amunesc", "4215000": "amunesc", "4215802": "amunesc",
    "4216206": "amunesc",
    # AMURC (5 municipios)
    "4204806": "amurc", "4205555": "amurc", "4213351": "amurc", "4215505": "amurc",
    "4216057": "amurc",
    # AMUREL (18 municipios)
    "4201505": "amurel", "4202800": "amurel", "4203956": "amurel", "4206108": "amurel",
    "4206207": "amurel", "4207205": "amurel", "4207304": "amurel", "4208807": "amurel",
    "4209409": "amurel", "4212403": "amurel", "4212650": "amurel", "4214904": "amurel",
    "4215455": "amurel", "4215604": "amurel", "4217006": "amurel", "4217105": "amurel",
    "4218400": "amurel", "4218707": "amurel",
    # AMURES (18 municipios)
    "4201000": "amures", "4202438": "amures", "4202503": "amures", "4202602": "amures",
    "4203253": "amures", "4203402": "amures", "4204178": "amures", "4204558": "amures",
    "4209300": "amures", "4211751": "amures", "4211892": "amures", "4212056": "amures",
    "4213302": "amures", "4215059": "amures", "4216503": "amures", "4216800": "amures",
    "4218905": "amures", "4218954": "amures",
    # AMVALI (7 municipios)
    "4202107": "amvali", "4204509": "amvali", "4206504": "amvali", "4208906": "amvali",
    "4210605": "amvali", "4216354": "amvali", "4217402": "amvali",
    # AMVE (14 municipios)
    "4201257": "amve", "4201703": "amve", "4202206": "amve", "4202404": "amve",
    "4202701": "amve", "4202909": "amve", "4205159": "amve", "4205902": "amve",
    "4206306": "amve", "4207502": "amve", "4213203": "amve", "4214706": "amve",
    "4215109": "amve", "4218202": "amve",
    # GRANFPOLIS (22 municipios)
    "4200606": "granfpolis", "4200705": "granfpolis", "4200903": "granfpolis",
    "4201109": "granfpolis", "4201208": "granfpolis", "4202305": "granfpolis",
    "4203709": "granfpolis", "4205407": "granfpolis", "4205704": "granfpolis",
    "4206009": "granfpolis", "4209805": "granfpolis", "4210209": "granfpolis",
    "4211504": "granfpolis", "4211900": "granfpolis", "4212304": "granfpolis",
    "4214300": "granfpolis", "4215703": "granfpolis", "4215901": "granfpolis",
    "4216305": "granfpolis", "4216602": "granfpolis", "4217253": "granfpolis",
    "4218004": "granfpolis",
}


class Command(BaseCommand):
    help = 'Carrega cidades de SC do IBGE e associa as regioes'

    def handle(self, *args, **options):
        url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios'
        self.stdout.write('Buscando municipios de SC do IBGE...')

        try:
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read()
                try:
                    data = raw.decode('utf-8')
                except UnicodeDecodeError:
                    data = gzip.decompress(raw).decode('utf-8')
                cities_data = json.loads(data)
        except Exception as e:
            self.stderr.write(f'Erro ao acessar IBGE API: {e}')
            return

        # Garantir que as regioes existem
        region_names = {
            'amai': 'Associação dos Municípios do Alto Irani',
            'amarp': 'Associação dos Municípios do Alto Vale do Rio do Peixe',
            'amauc': 'Associação dos Municípios do Alto Uruguai Catarinense',
            'amavi': 'Associação dos Municípios do Alto Vale do Itajaí',
            'ameosc': 'Associação dos Municípios do Extremo Oeste de SC',
            'amerios': 'Associação dos Municípios do Entre Rios',
            'amesc': 'Associação dos Municípios do Extremo Sul Catarinense',
            'amfri': 'Associação dos Municípios da Foz do Rio Itajaí',
            'ammoc': 'Associação dos Municípios do Meio Oeste Contestado',
            'amnoroeste': 'Associação dos Municípios do Noroeste Catarinense',
            'amosc': 'Associação dos Municípios do Oeste de SC',
            'amplanorte': 'Associação dos Municípios do Planalto Norte',
            'amplasc': 'Associação dos Municípios do Planalto Sul de SC',
            'amrec': 'Associação dos Municípios da Região Carbonífera',
            'amunesc': 'Associação dos Municípios do Nordeste de SC',
            'amurc': 'Associação dos Municípios da Região do Contestado',
            'amurel': 'Associação dos Municípios da Região de Laguna',
            'amures': 'Associação dos Municípios da Região Serrana',
            'amvali': 'Associação dos Municípios do Vale do Itapocu',
            'amve': 'Associação dos Municípios do Vale Europeu',
            'granfpolis': 'Associação dos Municípios da Grande Florianópolis',
        }

        regions = {}
        for slug, nome_completo in region_names.items():
            sigla = slug.upper()
            regiao, created = Regiao.objects.get_or_create(
                sigla=sigla,
                defaults={
                    'nome': nome_completo,
                    'nome_completo': nome_completo,
                    'slug': slug,
                },
            )
            if not regiao.slug:
                regiao.slug = slug
                regiao.nome_completo = nome_completo
                regiao.save(update_fields=['slug', 'nome_completo'])
            regions[slug] = regiao

        created_count = 0
        updated_count = 0
        skipped = 0

        for city_data in cities_data:
            ibge_code = str(city_data['id'])
            name = city_data['nome']
            slug = slugify(name)

            region_slug = CITY_REGION_MAP.get(ibge_code)
            if not region_slug or region_slug not in regions:
                self.stdout.write(f'  AVISO: {name} ({ibge_code}) sem regiao mapeada')
                skipped += 1
                continue

            regiao = regions[region_slug]

            # Tentar encontrar cidade existente por codigo_ibge ou por nome+regiao
            cidade = None
            try:
                cidade = Cidade.objects.get(codigo_ibge=ibge_code)
            except Cidade.DoesNotExist:
                try:
                    cidade = Cidade.objects.get(nome=name, regiao=regiao)
                except Cidade.DoesNotExist:
                    pass

            if cidade:
                cidade.codigo_ibge = ibge_code
                cidade.slug = slug
                cidade.nome = name
                cidade.regiao = regiao
                cidade.save(update_fields=['codigo_ibge', 'slug', 'nome', 'regiao'])
                updated_count += 1
            else:
                Cidade.objects.create(
                    nome=name,
                    slug=slug,
                    codigo_ibge=ibge_code,
                    regiao=regiao,
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Concluido: {created_count} criadas, {updated_count} atualizadas, {skipped} sem regiao'
        ))
