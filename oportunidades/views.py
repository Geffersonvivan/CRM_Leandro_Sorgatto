from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from usuarios.views import secao_required
from .models import Oportunidade


@secao_required('oportunidades')
def central(request):
    """Central de Oportunidades — lista as oportunidades vivas (Fase 1)."""
    qs = (Oportunidade.objects.filter(status__in=Oportunidade.VIVAS)
          .select_related('cidade', 'cidade__regiao'))
    f_tipo = request.GET.get('tipo') or ''
    f_prio = request.GET.get('prioridade') or ''
    if f_tipo:
        qs = qs.filter(tipo=f_tipo)
    if f_prio:
        qs = qs.filter(prioridade=f_prio)

    vivas = Oportunidade.objects.filter(status__in=Oportunidade.VIVAS)
    kpis = {
        'total': vivas.count(),
        'territorio': vivas.filter(tipo='territorio').count(),
        'relacionamento': vivas.filter(tipo='relacionamento').count(),
        'alta': vivas.filter(prioridade='alta').count(),
        'novas': vivas.filter(status='nova').count(),
    }
    return render(request, 'oportunidades/central.html', {
        'ops': list(qs), 'kpis': kpis, 'f_tipo': f_tipo, 'f_prio': f_prio,
        'tipos': Oportunidade.TIPO, 'prioridades': Oportunidade.PRIORIDADE,
    })


@secao_required('oportunidades')
def agendar(request, pk):
    """Marca em andamento e abre o compromisso já com a cidade preenchida."""
    o = get_object_or_404(Oportunidade, pk=pk)
    if o.status in ('nova', 'vista'):
        o.status = 'em_andamento'
        o.save(update_fields=['status', 'atualizada_em'])
    return redirect(f'/agenda/compromissos/?cidade={o.cidade_id or ""}')


@secao_required('oportunidades')
@require_POST
def descartar(request, pk):
    o = get_object_or_404(Oportunidade, pk=pk)
    o.motivo_descarte = (request.POST.get('motivo') or '')[:200]
    o.marcar_resolvida('descartada')
    return redirect(request.META.get('HTTP_REFERER') or 'oportunidades:central')
