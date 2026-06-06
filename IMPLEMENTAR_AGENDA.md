# Melhorias do Calendário/Agenda — Coração do CRM

## 1. Visualizações Avançadas

### 1.1 Vista semanal e diária
- Hoje só existe `dayGridMonth`. Adicionar `timeGridWeek` e `timeGridDay` no FullCalendar.
- Configuração trivial — já suportado pelo FullCalendar 6.1.15 instalado.

### 1.2 Vista de timeline por recurso
- Mostrar múltiplas agendas em paralelo (gabinete, pessoal, campanha) usando `resourceTimeline`.

### 1.3 Arrastar e soltar
- Habilitar `editable: true` no FullCalendar para reagendar compromissos arrastando.
- Infraestrutura de API já existe para atualizar datas.

---

## 2. Integração com o Mapa

### 2.1 Compromissos georreferenciados
- Ao criar compromisso vinculado a uma cidade, mostrar no mapa.
- Roteiro já tem coordenadas, mas compromissos avulsos não aparecem no mapa.

### 2.2 Sugestão inteligente de roteiro
- Ao ter 3+ compromissos no mesmo dia em cidades diferentes, sugerir automaticamente a criação de um Roteiro otimizado via OSRM.

### 2.3 Heatmap de presença
- Cruzar histórico de compromissos com cidades para identificar regiões pouco visitadas vs. muito visitadas.
- Alimentar o mapa de calor com dados de presença territorial.

---

## 3. Notificações e Lembretes

### 3.1 Lembretes antes do evento
- Hoje `Notificacao` existe mas não há envio antecipado (15min, 1h, 1 dia antes).
- Sem Celery, pode-se usar cron job ou `django-crontab`.

### 3.2 Resumo diário/semanal
- Email ou notificação PWA com agenda do dia seguinte e pendências.

### 3.3 Push notifications PWA
- Estrutura PWA já existe; falta implementar Web Push para lembretes em tempo real.

---

## 4. Gestão de Tarefas Pré/Pós-Compromisso

### 4.1 Checklist de preparação estruturado
- Hoje `preparacao` é texto livre. Transformar em modelo estruturado com itens marcáveis, responsáveis e prazos individuais.

### 4.2 Follow-up automatizado
- Campo `followup` existe mas é passivo. Após compromisso concluído, gerar automaticamente tarefas de follow-up com prazo.

### 4.3 Templates de compromisso
- Para tipos recorrentes (reunião de gabinete, visita a município, audiência pública), ter templates pré-configurados com checklist padrão.

---

## 5. Integração com Contatos/Apoiadores

### 5.1 Vincular participantes a apoiadores
- Hoje `participantes` é M2M com `User`. Permitir vincular `Apoiador` como participante externo, criando histórico de interações.

### 5.2 Histórico de reuniões por contato
- Na ficha do apoiador/liderança, mostrar timeline de todos os compromissos em que participou.

### 5.3 CRM activity tracking
- Cada compromisso concluído alimentar um score de relacionamento por cidade/região.

---

## 6. Recorrência e Séries

### 6.1 Eventos recorrentes
- Hoje cada compromisso é único. Implementar regras RRULE (semanal, mensal) para reuniões fixas como "gabinete toda segunda" ou "visita mensal à região X".

### 6.2 Séries de eventos
- Agrupar compromissos relacionados (ex: todas as audiências de um projeto de lei).

---

## 7. Sincronização Externa

### 7.1 Google Calendar sync
- Sincronização bidirecional via Google Calendar API. Importar compromissos pessoais e exportar agenda política.

### 7.2 iCal export
- Feed `.ics` por usuário para assinatura em qualquer app de calendário.

---

## 8. Analytics e Relatórios

### 8.1 Dashboard de produtividade
- Quantos compromissos por semana/mês, taxa de conclusão, tempo em cada tipo de atividade.

### 8.2 Cobertura territorial
- Cruzar compromissos × cidades para mostrar: "últimos 90 dias, X% das cidades de SC não receberam visita".

### 8.3 Funil de demandas
- De demanda recebida → compromisso agendado → realizado → follow-up concluído.

---

## Priorização Sugerida

| Prioridade | Item | Esforço | Seção |
|---|---|---|---|
| 1 | Vistas semana/dia no FullCalendar | Baixo | 1.1 |
| 2 | Drag & drop para reagendar | Baixo | 1.3 |
| 3 | Templates de compromisso | Médio | 4.3 |
| 4 | Vincular apoiadores como participantes | Médio | 5.1 |
| 5 | Heatmap de presença no mapa | Médio | 2.3 |
| 6 | Eventos recorrentes (RRULE) | Alto | 6.1 |
| 7 | Push notifications PWA | Alto | 3.3 |
| 8 | Google Calendar sync | Alto | 7.1 |

> Itens 1-2: configurações do FullCalendar já instalado — valor imediato.
> Itens 3-5: criam a ponte calendário ↔ CRM que faz dele o coração do sistema.
> Itens 6-8: estruturais, diferenciam de uma agenda simples.
