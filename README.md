# 🤖 Bot Noxis

Bot privado para gerenciamento, moderação e eventos do servidor.

---

## ✨ Funcionalidades

- **Moderação:** Sistema de advertências com cargos automáticos, banimento na 4ª advertência, e logs de todas as ações (`/advertir`, `/removeradv`, `/banir`, `/logs`).
- **Eventos:** Criação de eventos com botão de inscrição, formulário para registro de personagem e visualização de inscritos (`/evento`, `/inscritos`).
- **Anúncios:** Comandos para comunicados gerais e de eventos com menção `@here` (`/anunciar`, `/evento`).
- **Engajamento:** Mensagem de boas-vindas em embed, reações automáticas com emojis do servidor e comando motivacional (`/motivar`).
- **Administração:** Recarregamento de módulos em tempo real sem desligar o bot (`/reload`).

---

## 🎮 Comandos Principais

| Comando | Parâmetros | Descrição |
| :--- | :--- | :--- |
| `/anunciar` | `titulo`, `mensagem` | Envia um anúncio geral formatado. |
| `/evento` | `nome`, `data_hora`, `local` | Cria um novo evento com botão de inscrição. |
| `/inscritos` | Nenhum | Exibe a lista de inscritos em todos os eventos ativos. |
| `/advertir` | `membro`, `motivo` | Adverte um membro e atribui o cargo correspondente. |
| `/removeradv`| `membro`, `numero`, `motivo_revogacao` | Remove uma advertência de um membro. |
| `/veravisos`| `membro` | Mostra as advertências ativas de um membro. |
| `/banir` | `membro`, `motivo` | Bane um membro manualmente. |
| `/logs advertencias` | `membro` | Mostra o histórico de advertências de um membro. |
| `/logs bans` | `membro` | Mostra o histórico de bans de um membro. |
| `/reload` | `cog` (opcional) | Recarrega as funcionalidades do bot (só para o dono). |
| `/motivar` | Nenhum | Envia uma citação motivacional. |

---

## ⚙️ Guia de Configuração Rápida

Para alterar as configurações principais, edite as seguintes variáveis nos arquivos:

- **`bot.py`**
  - `TOKEN`: O token secreto do seu bot.

- **`cogs/admin.py`**
  - `self.adv_roles`: Dicionário com os IDs dos cargos de 1ª, 2ª e 3ª advertência.

- **`cogs/anuncio.py`**
  - `CANAL_ANUNCIOS_ID`: ID do canal para onde vão os anúncios gerais.

- **`cogs/boas_vindas.py`**
  - `CANAL_BOAS_VINDAS_NOME`: Nome exato do canal de boas-vindas.
  - `CANAL_REGRAS_ID`: ID do canal de regras para o link.
  - `IMAGENS_BEMVINDO`: Lista de URLs de imagens/GIFs para o banner.

- **`cogs/evento.py`**
  - `CANAL_EVENTOS_ID`: ID do canal para onde vão os anúncios de eventos.

- **`cogs/reacoes.py`**
  - `NOMES_EMOJIS_PERSONALIZADOS`: Lista com os nomes dos emojis do servidor a serem usados nas reações.

---

## 🚀 Como Ligar e Atualizar o Bot

- **Para Ligar:** Execute o arquivo `iniciar_bot.bat`.
- **Para Atualizar o Código:**
  - Se você editou um Cog (ex: `admin.py`), use o comando `/reload` no Discord.
  - Se você adicionou um arquivo `.py` novo, reinicie o bot fechando e abrindo o `iniciar_bot.bat`.