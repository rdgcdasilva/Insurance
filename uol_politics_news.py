"""
Rotina de atualização de notícias de política do UOL.

Busca notícias via feed RSS do UOL Política, salva em JSON e
mantém um histórico com deduplicação por link.

Uso:
    python uol_politics_news.py               # execução única
    python uol_politics_news.py --schedule 30 # atualiza a cada 30 minutos
"""

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

RSS_URL = "https://rss.uol.com.br/feed/politica.xml"
OUTPUT_FILE = Path("uol_politica_noticias.json")
LOG_FILE = Path("uol_politics_news.log")
MAX_SAVED_ITEMS = 500  # limite de notícias mantidas no arquivo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------


def fetch_news(url: str) -> list[dict]:
    """Busca e parseia o feed RSS retornando lista de notícias."""
    log.info("Buscando feed: %s", url)
    feed = feedparser.parse(url)

    if feed.bozo:
        raise ValueError(f"Erro ao parsear feed RSS: {feed.bozo_exception}")

    items = []
    for entry in feed.entries:
        published_raw = entry.get("published_parsed") or entry.get("updated_parsed")
        published = (
            datetime(*published_raw[:6], tzinfo=timezone.utc).isoformat()
            if published_raw
            else None
        )

        items.append(
            {
                "titulo": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "resumo": _clean_html(entry.get("summary", "")),
                "publicado_em": published,
                "autor": entry.get("author", "").strip(),
                "tags": [t.get("term", "") for t in entry.get("tags", [])],
            }
        )

    log.info("%d notícias encontradas no feed.", len(items))
    return items


def load_existing(path: Path) -> dict:
    """Carrega o arquivo JSON existente ou retorna estrutura vazia."""
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {"ultima_atualizacao": None, "total": 0, "noticias": []}


def merge_news(existing: list[dict], fresh: list[dict]) -> tuple[list[dict], int]:
    """
    Mescla notícias novas com as existentes, removendo duplicatas por link.
    Retorna (lista_mesclada, quantidade_adicionada).
    """
    seen_links = {n["link"] for n in existing}
    new_items = [n for n in fresh if n["link"] not in seen_links]
    merged = new_items + existing
    return merged[:MAX_SAVED_ITEMS], len(new_items)


def save(path: Path, data: dict) -> None:
    """Salva o arquivo JSON com indentação legível."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("Arquivo salvo: %s (%d notícias)", path, data["total"])


def _clean_html(text: str) -> str:
    """Remove tags HTML simples do texto."""
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def update_once() -> None:
    """Executa uma rodada completa de atualização."""
    try:
        fresh = fetch_news(RSS_URL)
        data = load_existing(OUTPUT_FILE)
        merged, added = merge_news(data["noticias"], fresh)

        data["noticias"] = merged
        data["total"] = len(merged)
        data["ultima_atualizacao"] = datetime.now(timezone.utc).isoformat()

        save(OUTPUT_FILE, data)

        if added:
            log.info("%d nova(s) notícia(s) adicionada(s).", added)
        else:
            log.info("Nenhuma notícia nova encontrada.")

    except Exception as exc:
        log.error("Falha na atualização: %s", exc)
        raise


def run_scheduler(interval_minutes: int) -> None:
    """Loop contínuo que executa update_once a cada `interval_minutes`."""
    log.info("Agendador iniciado — intervalo: %d minuto(s).", interval_minutes)
    while True:
        update_once()
        log.info("Próxima atualização em %d minuto(s).", interval_minutes)
        time.sleep(interval_minutes * 60)


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atualiza notícias de política do UOL."
    )
    parser.add_argument(
        "--schedule",
        type=int,
        metavar="MINUTOS",
        help="Executa em loop com intervalo em minutos (ex: --schedule 30).",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduler(args.schedule)
    else:
        update_once()


if __name__ == "__main__":
    main()
