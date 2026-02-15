"""
Processador de arquivos de documentos.

Implementação concreta para extração de texto,
metadados e detecção de seções.

Suporta: PDF (PyPDF2), Word (.docx), OpenOffice (.odt),
e LaTeX (.tex).
"""

import logging
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

from ...core.interfaces.services.i_pdf_processor import (
    IPdfProcessor,
    SecaoDetectada,
)
from ...core.value_objects.metadados_pdf import (
    MetadadosPDF,
)
from ...core.exceptions.pdf_exceptions import (
    PDFInvalidoException,
    PDFProtegidoException,
    ExtracaoException,
)

logger = logging.getLogger(__name__)

# Extensões suportadas
EXTENSOES_SUPORTADAS = {".pdf", ".docx", ".odt", ".tex", ".md"}

# Padrões para detecção de seções em textos estruturados
PADRAO_SECAO = re.compile(
    r"^(\d+(?:\.\d+)*\.?)\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ].*)",
    re.MULTILINE,
)
PADRAO_SECAO_DESCRITIVA = re.compile(
    r"^(I{1,3}V?|V?I{0,3})\s*[-–.]\s*(.+)",
    re.MULTILINE,
)
PADRAO_SECAO_MARKDOWN = re.compile(
    r"^(#{1,6})\s+(.+)",
    re.MULTILINE,
)


class PdfProcessor(IPdfProcessor):
    """
    Processador de documentos para textos estruturados.

    Extrai texto, metadados e detecta seções em
    PDF, Word (.docx), OpenOffice (.odt) e LaTeX (.tex).
    """

    # ── Validação ──────────────────────────────

    async def validar_pdf(
        self, caminho: str
    ) -> bool:
        """Valida se o arquivo é suportado."""
        try:
            path = Path(caminho)
            if not path.exists():
                return False
            if path.suffix.lower() not in EXTENSOES_SUPORTADAS:
                return False
            if path.stat().st_size == 0:
                return False

            ext = path.suffix.lower()

            if ext == ".pdf":
                return await self._validar_pdf(path)
            elif ext == ".docx":
                return self._validar_docx(path)
            elif ext == ".odt":
                return self._validar_odt(path)
            elif ext == ".tex":
                return self._validar_tex(path)
            elif ext == ".md":
                return self._validar_md(path)

            return False

        except Exception as e:
            logger.error(
                f"Arquivo inválido: {caminho}: {e}"
            )
            return False

    async def _validar_pdf(self, path: Path) -> bool:
        """Valida PDF."""
        if PdfReader is None:
            logger.warning("PyPDF2 não instalado")
            return True
        reader = PdfReader(str(path))
        _ = len(reader.pages)
        return True

    def _validar_docx(self, path: Path) -> bool:
        """Valida .docx (é um zip com word/document.xml)."""
        try:
            with zipfile.ZipFile(str(path), "r") as z:
                return "word/document.xml" in z.namelist()
        except zipfile.BadZipFile:
            return False

    def _validar_odt(self, path: Path) -> bool:
        """Valida .odt (é um zip com content.xml)."""
        try:
            with zipfile.ZipFile(str(path), "r") as z:
                return "content.xml" in z.namelist()
        except zipfile.BadZipFile:
            return False

    def _validar_tex(self, path: Path) -> bool:
        """Valida .tex (texto legível com comandos LaTeX)."""
        try:
            texto = path.read_text(
                encoding="utf-8", errors="ignore"
            )
            # Verificar se parece LaTeX
            return (
                "\\begin" in texto
                or "\\document" in texto
                or "\\section" in texto
                or len(texto) > 10
            )
        except Exception:
            return False

    def _validar_md(self, path: Path) -> bool:
        """Valida .md (texto legível em Markdown)."""
        try:
            texto = path.read_text(
                encoding="utf-8", errors="ignore"
            )
            return len(texto.strip()) > 0
        except Exception:
            return False

    # ── Extração de texto ──────────────────────

    async def extrair_texto(
        self, caminho: str
    ) -> str:
        """Extrai texto completo do documento."""
        path = Path(caminho)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return await self._extrair_texto_pdf(caminho)
        elif ext == ".docx":
            return self._extrair_texto_docx(caminho)
        elif ext == ".odt":
            return self._extrair_texto_odt(caminho)
        elif ext == ".tex":
            return self._extrair_texto_tex(caminho)
        elif ext == ".md":
            return self._extrair_texto_md(caminho)
        else:
            raise ExtracaoException(
                f"Formato não suportado: {ext}"
            )

    async def _extrair_texto_pdf(
        self, caminho: str
    ) -> str:
        """Extrai texto de PDF usando PyPDF2."""
        if PdfReader is None:
            raise ExtracaoException(
                "PyPDF2 não está instalado"
            )

        try:
            reader = PdfReader(caminho)

            if reader.is_encrypted:
                raise PDFProtegidoException(
                    f"PDF protegido: {caminho}"
                )

            paginas_texto: List[str] = []
            for i, pagina in enumerate(
                reader.pages, 1
            ):
                texto = pagina.extract_text()
                if texto:
                    paginas_texto.append(
                        f"--- Página {i} ---\n{texto}"
                    )

            texto_completo = "\n\n".join(
                paginas_texto
            )

            logger.info(
                f"PDF: extraídos {len(texto_completo)} chars "
                f"de {len(reader.pages)} páginas"
            )

            return texto_completo

        except PDFProtegidoException:
            raise
        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair texto do PDF: {e}"
            )

    def _extrair_texto_docx(
        self, caminho: str
    ) -> str:
        """Extrai texto de Word (.docx) via XML."""
        try:
            with zipfile.ZipFile(caminho, "r") as z:
                xml_content = z.read(
                    "word/document.xml"
                )

            # Namespace do Word
            ns = {
                "w": (
                    "http://schemas.openxmlformats.org"
                    "/wordprocessingml/2006/main"
                ),
            }

            root = ET.fromstring(xml_content)
            paragrafos = []
            for p in root.iter(f"{{{ns['w']}}}p"):
                textos = []
                for t in p.iter(f"{{{ns['w']}}}t"):
                    if t.text:
                        textos.append(t.text)
                if textos:
                    paragrafos.append(
                        "".join(textos)
                    )

            texto = "\n\n".join(paragrafos)

            logger.info(
                f"DOCX: extraídos {len(texto)} chars "
                f"de {len(paragrafos)} parágrafos"
            )
            return texto

        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair texto do DOCX: {e}"
            )

    def _extrair_texto_odt(
        self, caminho: str
    ) -> str:
        """Extrai texto de OpenDocument (.odt) via XML."""
        try:
            with zipfile.ZipFile(caminho, "r") as z:
                xml_content = z.read("content.xml")

            root = ET.fromstring(xml_content)

            # Coletar todo o texto recursivamente
            def _extrair_textos(elem):
                textos = []
                if elem.text:
                    textos.append(elem.text)
                for child in elem:
                    textos.extend(
                        _extrair_textos(child)
                    )
                    if child.tail:
                        textos.append(child.tail)
                return textos

            # Namespaces do ODF
            ns_text = (
                "urn:oasis:names:tc:opendocument"
                ":xmlns:text:1.0"
            )
            paragrafos = []
            for p in root.iter(f"{{{ns_text}}}p"):
                partes = _extrair_textos(p)
                linha = "".join(partes).strip()
                if linha:
                    paragrafos.append(linha)

            texto = "\n\n".join(paragrafos)

            logger.info(
                f"ODT: extraídos {len(texto)} chars "
                f"de {len(paragrafos)} parágrafos"
            )
            return texto

        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair texto do ODT: {e}"
            )

    def _extrair_texto_tex(
        self, caminho: str
    ) -> str:
        """
        Extrai texto de LaTeX (.tex).

        Remove comandos LaTeX comuns, mantendo o
        conteúdo textual para revisão.
        """
        try:
            texto_raw = Path(caminho).read_text(
                encoding="utf-8", errors="ignore"
            )

            # Extrair apenas o corpo do documento
            match_body = re.search(
                r"\\begin\{document\}(.*?)\\end\{document\}",
                texto_raw,
                re.DOTALL,
            )
            if match_body:
                texto = match_body.group(1)
            else:
                texto = texto_raw

            # Remover comentários LaTeX (linhas que começam com %)
            texto = re.sub(
                r"(?m)^%.*$", "", texto
            )
            texto = re.sub(
                r"(?<!\\)%.*$", "", texto,
                flags=re.MULTILINE,
            )

            # Substituir comandos de seção por marcadores
            texto = re.sub(
                r"\\section\{([^}]+)\}",
                r"\n\n## \1\n\n", texto,
            )
            texto = re.sub(
                r"\\subsection\{([^}]+)\}",
                r"\n\n### \1\n\n", texto,
            )
            texto = re.sub(
                r"\\subsubsection\{([^}]+)\}",
                r"\n\n#### \1\n\n", texto,
            )
            texto = re.sub(
                r"\\chapter\{([^}]+)\}",
                r"\n\n# \1\n\n", texto,
            )

            # Remover comandos LaTeX comuns
            # \textbf{X} → X, \textit{X} → X, etc.
            texto = re.sub(
                r"\\(?:textbf|textit|emph|underline|"
                r"textrm|textsc|textsf|texttt)"
                r"\{([^}]+)\}",
                r"\1", texto,
            )

            # Remover environments preservando conteúdo
            texto = re.sub(
                r"\\begin\{(?:itemize|enumerate|"
                r"description|quote|quotation|"
                r"center|flushleft|flushright)\}",
                "", texto,
            )
            texto = re.sub(
                r"\\end\{(?:itemize|enumerate|"
                r"description|quote|quotation|"
                r"center|flushleft|flushright)\}",
                "", texto,
            )

            # \item → bullet
            texto = re.sub(
                r"\\item\b\s*", "• ", texto
            )

            # Remover outros comandos simples
            texto = re.sub(
                r"\\(?:label|ref|cite|pageref|"
                r"footnote|index|bibliography"
                r"style|bibliography|usepackage|"
                r"documentclass|maketitle|"
                r"tableofcontents|newpage|"
                r"clearpage|vspace|hspace|"
                r"noindent|par)\b"
                r"(?:\{[^}]*\})*(?:\[[^\]]*\])*",
                "", texto,
            )

            # Limpar espaços excessivos
            texto = re.sub(
                r"\n{3,}", "\n\n", texto
            )
            texto = texto.strip()

            logger.info(
                f"TEX: extraídos {len(texto)} chars "
                f"(raw: {len(texto_raw)} chars)"
            )
            return texto

        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair texto do TEX: {e}"
            )

    def _extrair_texto_md(
        self, caminho: str
    ) -> str:
        """
        Extrai texto de Markdown (.md).

        Remove sintaxe Markdown decorativa, mantendo
        o conteúdo textual e a estrutura de seções.
        """
        try:
            texto_raw = Path(caminho).read_text(
                encoding="utf-8", errors="ignore"
            )

            texto = texto_raw

            # Remover imagens inline ![alt](url)
            texto = re.sub(
                r"!\[[^\]]*\]\([^)]+\)", "", texto
            )

            # Converter links [texto](url) → texto
            texto = re.sub(
                r"\[([^\]]+)\]\([^)]+\)",
                r"\1", texto,
            )

            # Remover marcadores de negrito/itálico
            texto = re.sub(
                r"\*{1,3}([^*]+)\*{1,3}",
                r"\1", texto,
            )
            texto = re.sub(
                r"_{1,3}([^_]+)_{1,3}",
                r"\1", texto,
            )

            # Remover blocos de código (``` ... ```)
            texto = re.sub(
                r"```[^`]*```", "", texto,
                flags=re.DOTALL,
            )

            # Remover código inline `código`
            texto = re.sub(
                r"`([^`]+)`", r"\1", texto
            )

            # Remover linhas horizontais (---, ***)
            texto = re.sub(
                r"^[-*_]{3,}\s*$", "",
                texto, flags=re.MULTILINE,
            )

            # Limpar espaços excessivos
            texto = re.sub(
                r"\n{3,}", "\n\n", texto
            )
            texto = texto.strip()

            logger.info(
                f"MD: extraídos {len(texto)} chars "
                f"(raw: {len(texto_raw)} chars)"
            )
            return texto

        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair texto do MD: {e}"
            )

    # ── Metadados ──────────────────────────────

    async def extrair_metadados(
        self, caminho: str
    ) -> MetadadosPDF:
        """Extrai metadados do documento."""
        path = Path(caminho)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return await self._extrair_metadados_pdf(
                caminho
            )
        else:
            # Metadados genéricos para DOCX/ODT/TEX
            return MetadadosPDF(
                numero_paginas=1,
                tamanho_bytes=path.stat().st_size
                if path.exists()
                else 0,
                titulo=path.stem,
            )

    async def _extrair_metadados_pdf(
        self, caminho: str
    ) -> MetadadosPDF:
        """Extrai metadados de PDF."""
        if PdfReader is None:
            path = Path(caminho)
            n_paginas = 1
            try:
                raw = path.read_bytes()
                n_paginas = max(
                    1,
                    raw.count(b"/Type /Page")
                    - raw.count(b"/Type /Pages"),
                )
            except Exception:
                pass
            return MetadadosPDF(
                numero_paginas=n_paginas,
                tamanho_bytes=path.stat().st_size
                if path.exists()
                else 0,
            )

        try:
            reader = PdfReader(caminho)
            meta = reader.metadata or {}
            path = Path(caminho)

            data_criacao = None
            if hasattr(meta, "creation_date"):
                data_criacao = meta.creation_date

            data_mod = None
            if hasattr(meta, "modification_date"):
                data_mod = meta.modification_date

            return MetadadosPDF(
                numero_paginas=len(reader.pages),
                titulo=getattr(
                    meta, "title", None
                ),
                autor=getattr(
                    meta, "author", None
                ),
                criador=getattr(
                    meta, "creator", None
                ),
                produtor=getattr(
                    meta, "producer", None
                ),
                data_criacao=data_criacao,
                data_modificacao=data_mod,
                tamanho_bytes=path.stat().st_size,
                criptografado=reader.is_encrypted,
            )

        except Exception as e:
            logger.error(
                f"Erro ao extrair metadados: {e}"
            )
            return MetadadosPDF(numero_paginas=1)

    # ── Detecção de seções ─────────────────────

    async def detectar_secoes(
        self,
        texto: str,
        numero_paginas: int = 0,
    ) -> List[SecaoDetectada]:
        """
        Detecta seções no texto extraído.

        Usa padrões de numeração de textos estruturados
        (1. TÍTULO, 1.1 SUBTÍTULO, etc.)
        """
        secoes: List[SecaoDetectada] = []

        # Buscar padrões de seção numerada
        matches = list(PADRAO_SECAO.finditer(texto))

        if not matches:
            # Fallback: seções descritivas (I, II, III...)
            matches = list(
                PADRAO_SECAO_DESCRITIVA.finditer(texto)
            )

        # Fallback: headings Markdown (# Título)
        usa_md = False
        if not matches:
            matches = list(
                PADRAO_SECAO_MARKDOWN.finditer(texto)
            )
            usa_md = bool(matches)

        if not matches:
            # Sem seções detectadas
            secoes.append(
                SecaoDetectada(
                    titulo="DOCUMENTO COMPLETO",
                    conteudo=texto,
                    pagina_inicio=1,
                    pagina_fim=max(1, numero_paginas),
                    nivel=1,
                )
            )
            return secoes

        for i, match in enumerate(matches):
            grupo1 = match.group(1).strip()
            titulo_texto = match.group(2).strip()
            if usa_md:
                nivel = len(grupo1)  # contagem de #
                titulo = titulo_texto
            else:
                nivel = grupo1.count(".") + 1
                titulo = f"{grupo1} {titulo_texto}"

            # Determinar conteúdo da seção
            inicio = match.end()
            if i + 1 < len(matches):
                fim = matches[i + 1].start()
            else:
                fim = len(texto)

            conteudo = texto[inicio:fim].strip()

            # Estimar páginas (aprox 3000 chars/página)
            pos_inicio = match.start()
            pag_inicio = max(
                1, pos_inicio // 3000 + 1
            )
            pag_fim = max(
                pag_inicio, fim // 3000 + 1
            )
            if numero_paginas > 0:
                pag_fim = min(
                    pag_fim, numero_paginas
                )

            if conteudo:
                secoes.append(
                    SecaoDetectada(
                        titulo=titulo,
                        conteudo=conteudo,
                        pagina_inicio=pag_inicio,
                        pagina_fim=pag_fim,
                        nivel=nivel,
                    )
                )

        logger.info(
            f"Detectadas {len(secoes)} seções"
        )

        return secoes

    # ── Extração por página ────────────────────

    async def extrair_texto_por_pagina(
        self, caminho: str, pagina: int
    ) -> str:
        """Extrai texto de uma página específica."""
        path = Path(caminho)
        ext = path.suffix.lower()

        if ext != ".pdf":
            # Para não-PDF, retornar texto completo
            # (não têm conceito de página)
            texto = await self.extrair_texto(caminho)
            logger.info(
                f"Formato {ext}: retornando texto "
                f"completo (sem paginação)"
            )
            return texto

        if PdfReader is None:
            raise ExtracaoException(
                "PyPDF2 não instalado"
            )

        try:
            reader = PdfReader(caminho)
            if pagina < 1 or pagina > len(
                reader.pages
            ):
                raise ExtracaoException(
                    f"Página {pagina} fora do intervalo"
                    f" (1-{len(reader.pages)})"
                )

            texto = reader.pages[
                pagina - 1
            ].extract_text()
            return texto or ""

        except ExtracaoException:
            raise
        except Exception as e:
            raise ExtracaoException(
                f"Erro ao extrair página {pagina}: {e}"
            )
