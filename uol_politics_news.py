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
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

RSS_URL = "https://rss.uol.com.br/feed/politica.xml"
OUTPUT_FILE = Path("uol_politica_noticias.json")
LOG_FILE = Path("uol_politics_news.log")
MAX_SAVED_ITEMS = 500
REQUEST_TIMEOUT = 15

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


def fetch_feed_xml(url: str) -> str:
    """Faz download do feed RSS e retorna o conteúdo como string."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; UOLPoliticsBot/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_feed(xml_content: str) -> list[dict]:
    """Parseia o XML RSS e extrai os campos relevantes de cada item."""
    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Feed RSS inválido: elemento <channel> não encontrado.")

    items = []
    for item in channel.findall("item"):

        def text(tag: str) -> str:
            el = item.find(tag)
            return (el.text or "").strip() if el is not None else ""

        pub_date_raw = text("pubDate")
        try:
            published = parsedate_to_datetime(pub_date_raw).isoformat() if pub_date_raw else None
        except Exception:
            published = pub_date_raw or None

        items.append(
            {
                "titulo": text("title"),
                "link": text("link"),
                "resumo": _clean_html(text("description")),
                "publicado_em": published,
                "autor": text("{http://purl.org/dc/elements/1.1/}creator") or text("author"),
                "categoria": text("category"),
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
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def update_once() -> None:
    """Executa uma rodada completa de atualização."""
    log.info("Buscando feed: %s", RSS_URL)
    try:
        xml_content = fetch_feed_xml(RSS_URL)
        fresh = parse_feed(xml_content)
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
