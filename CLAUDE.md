# Dashboard Escritório — Taques Advogados

## Sobre o projeto

Dashboard web para gestão de casos jurídicos do escritório Taques Advogados. O sistema centraliza dados de 206+ casos com filtros, métricas, gráficos e edição de status em tempo real.

O usuário principal (Lenon) é advogado, não programador. Todas as explicações devem ser claras e diretas. Ao fazer alterações, sempre faça commit e push para que o deploy automático funcione.

## Stack tecnológico

- **Front-end:** Streamlit (Python)
- **Banco de dados:** Supabase (PostgreSQL hospedado)
- **Hospedagem:** Streamlit Community Cloud (deploy automático via GitHub)
- **Versionamento:** GitHub (`taqueslenon-beep/dashboard-escritorio`, branch `main`)

## URLs importantes

- **App em produção:** https://dashboard-escritorio-naagpzchomkeuyl5teqgbm.streamlit.app/
- **Supabase:** https://tjpasfrzsogdhxnerxhs.supabase.co
- **GitHub:** https://github.com/taqueslenon-beep/dashboard-escritorio

## Identidade visual

- Cor principal (verde): `#223631`
- Cor verde claro: `#2d4a3e`
- Fundo off-white: `#f5f3ef`
- Fundo creme: `#eae6df`
- Fonte: Inter (Google Fonts)
- Sidebar: fundo verde escuro com texto branco
- Cards/métricas: fundo branco com borda verde à esquerda

## Estrutura atual do banco de dados (Supabase)

### Tabela `casos` (existente — 206 registros)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | int | Chave primária |
| nome_do_caso | text | Nome do caso |
| cliente | text | Nome do cliente |
| nucleo | text | AMBIENTAL, COBRANÇAS, GENERALISTA |
| responsavel | text | LENON, GILBERTO |
| prioridade | text | P1, P2, P3, P4 |
| status | text | EM ANDAMENTO, CONCLUIDO, etc. |
| grupo | text | Agrupamento do caso |

### Tabelas planejadas (ainda não criadas)
- `clientes` — Cadastro completo de clientes (nome, cpf_cnpj, email, telefone)
- `casos_clientes` — Vínculo N:N entre casos e clientes
- `processos` — Processos vinculados a cada caso (numero, tribunal, vara, tipo_acao, fase)
- `prazos` — Prazos processuais vinculados a processos
- `audiencias` — Audiências e compromissos vinculados a processos

## Hierarquia de dados

```
Escritório
└── Caso (guarda-chuva)
    ├── Cliente(s) — um caso pode ter vários clientes
    └── Processo(s) — um caso agrupa vários processos
        ├── Prazo(s) — cada processo tem prazos
        └── Audiência(s) — cada processo tem audiências
```

## Arquitetura do app (app.py)

O app tem 2 páginas navegáveis via `streamlit-option-menu` na sidebar:

1. **Dashboard** — Métricas (Total, P1, Ambiental, Lenon, Gilberto) + 4 gráficos Plotly (pizza núcleo, barras prioridade, pizza status, barras empilhadas responsável×núcleo)
2. **Casos** — Duas sub-abas:
   - "Tabela" — Dataframe completo com exportação CSV
   - "Editar Status" — Cards individuais com selectbox para alterar status (salva automaticamente no Supabase)

## Fluxo de deploy

```
Editar código → git add → git commit → git push → Streamlit Cloud faz redeploy automático
```

Toda alteração que for feita no código deve ser commitada e pushada. O Streamlit Cloud detecta o push e faz redeploy em ~1 minuto.

## Documentação no Obsidian

O projeto tem documentação no Obsidian do Lenon em:
```
Obsidian do Lenon/1-projetos/lista-de-projetos/organizacao-dados-escritorio/
├── 0-projeto.md              — Documentação principal, tarefas e checklist
├── 1-diagrama-estrutura-dados.md — Diagramas Mermaid (ER, fluxo, fontes de dados)
└── 2-guia-claude-code.md     — Guia de setup e desenvolvimento
```

Quando o Lenon pedir para atualizar a documentação do projeto, editar esses arquivos no caminho acima.

## Padrões de código

- Usar português para nomes de variáveis e comentários
- Separar seções com comentários `# ── Nome ──────`
- Manter as cores como constantes no topo do arquivo (VERDE, VERDE_CLARO, OFF_WHITE, CREME)
- Usar f-strings para CSS dinâmico
- Usar `st.cache_resource` para conexão com Supabase
- Usar `st.session_state` para cache de dados

## Comandos úteis

```bash
# Rodar localmente
streamlit run app.py

# Ver o que mudou
git status
git diff

# Commitar e fazer deploy
git add -A
git commit -m "descrição da mudança"
git push

# Criar tabela no Supabase (exemplo)
# Usar o painel do Supabase ou a API Python
```

## Status das opções de status dos casos

```python
STATUS_OPTIONS = [
    "EM ANDAMENTO", "CONCLUIDO", "AGUARDANDO CLIENTE",
    "AGUARDANDO TRIBUNAL", "EM RECURSO", "SUSPENSO",
    "ARQUIVADO", "EM MONITORAMENTO", "SUBSTABELECIDO", "SEM STATUS"
]
```

## Próximos passos do projeto

1. Criar tabelas novas no Supabase (clientes, processos, prazos, audiências)
2. Migrar dados de Firebase, planilhas e Google Drives para o Supabase
3. Adicionar novas páginas ao dashboard (Clientes, Processos, Prazos)
4. Implementar sistema de busca e filtros avançados
5. Migrar secrets para variáveis de ambiente (Streamlit Secrets)
