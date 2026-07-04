# Configs de marca (D10 — docs/ARQUITETURA_ROADMAP.md, Fase 1).
# Cada configs/<slug>.py define CAMPANHA para uma marca; o settings carrega
# conforme a env MARCA=<slug>. Config de marca não é segredo: fica versionada
# e revisável. Segredo (chave, banco, API) continua só em env.
