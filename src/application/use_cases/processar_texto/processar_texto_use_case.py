"""
Caso de uso: Processar Texto Estruturado.

Orquestra o processamento completo de um texto estruturado,
desde a leitura do arquivo até a geração dos relatórios.
"""

import asyncio
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List

from ....core.entities.texto_estruturado import TextoEstruturado
from ....core.entities.secao import Secao
from ....core.enums.status_texto import StatusTexto
from ....core.interfaces.services.i_pdf_processor import (
    IPdfProcessor,
)
from ....core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ....core.interfaces.services.i_report_generator import (
    IReportGenerator,
)
from ....core.interfaces.services.i_logger import (
    ILogger,
)
from ....core.interfaces.repositories.i_texto_repository import (
    ITextoRepository,
)
from ....core.interfaces.repositories.i_config_repository import (
    IConfigRepository,
)
from ....core.validators.texto_validator import (
    TextoValidator,
)
from ....core.exceptions.texto_exceptions import (
    TextoInvalidoException,
)
from ..revisar_secao.revisar_secao_use_case import (
    RevisarSecaoUseCase,
)
from ..gerar_relatorio.gerar_relatorio_use_case import (
    GerarRelatorioUseCase,
)
from ..verificar_consistencia.verificar_consistencia_use_case import (  # noqa: E501
    VerificarConsistenciaUseCase,
)
from .dto import (
    ProcessarTextoInputDTO,
    ProcessarTextoOutputDTO,
    ProgressoDTO,
)


class ProcessarTextoUseCase:
    """
    Caso de uso principal: processamento completo de texto.

    Orquestra todas as etapas do pipeline de revisão:
    1. Carregamento e validação do documento
    2. Extração de texto e detecção de seções
    3. Revisão iterativa (gramatical + técnica)
    4. Validação das correções
    5. Verificação de consistência entre seções
    6. Síntese final
    7. Geração de relatórios
    """

    def __init__(
        self,
        pdf_processor: IPdfProcessor,
        agentes_revisores: List[IAIAgent],
        agente_validador: IAIAgent,
        agente_consistencia: IAIAgent,
        texto_repo: ITextoRepository,
        config_repo: IConfigRepository,
        geradores_relatorio: Dict[
            str, IReportGenerator
        ],
        logger: ILogger,
        callback_progresso: Optional[
            Callable[[ProgressoDTO], None]
        ] = None,
    ) -> None:
        self._pdf_processor = pdf_processor
        self._agentes_revisores = agentes_revisores
        self._agente_validador = agente_validador
        self._agente_consistencia = (
            agente_consistencia
        )
        self._texto_repo = texto_repo
        self._config_repo = config_repo
        self._geradores_relatorio = (
            geradores_relatorio
        )
        self._logger = logger
        self._callback_progresso = callback_progresso

        # Compor sub-use-cases — um por agente revisor
        self._ucs_revisar = []
        for agente in agentes_revisores:
            self._ucs_revisar.append(
                RevisarSecaoUseCase(
                    agente=agente,
                    config_repo=config_repo,
                    logger=logger,
                )
            )

        self._uc_relatorio = GerarRelatorioUseCase(
            geradores=geradores_relatorio,
            logger=logger,
        )
        self._uc_consistencia = (
            VerificarConsistenciaUseCase(
                agente=agente_consistencia,
                logger=logger,
            )
        )
        # Validador de negócio
        self._validator = TextoValidator()

    async def executar(
        self, input_dto: ProcessarTextoInputDTO
    ) -> ProcessarTextoOutputDTO:
        """
        Executa o processamento completo do texto.

        Args:
            input_dto: Dados de entrada

        Returns:
            DTO com resultados do processamento
        """
        try:
            self._logger.info(
                f"Iniciando processamento: "
                f"{input_dto.caminho_arquivo}"
            )

            # Carregar configuração para verificar modo
            config = self._config_repo.carregar_configuracao()
            modo_proc = config.get(
                "modo_processamento", "texto_completo"
            )
            # Verificar IA em uso para logs
            info_ia = {"provedor": "Desconhecido", "modelo": "Desconhecido"}
            agente = self._agentes_revisores[0]
            if hasattr(agente, "_gateway") and agente._gateway:
                 info_ia = agente._gateway.obter_info_modelo()

            mock_label = " [MOCK]" if getattr(
                self._agentes_revisores[0], '_gateway', None
            ) and self._agentes_revisores[0]._gateway._modo_mock else ""

            msg_inicio = (
                f"Iniciando pipeline de revisão{mock_label} | "
                f"IA: {info_ia['provedor']} ({info_ia['modelo']})"
            )

            self._notificar_progresso("inicio", 0, msg_inicio)

            # Etapa 1: Carregar e validar documento
            self._notificar_progresso(
                "carregamento", 5, "Carregando documento..."
            )
            texto = await self._carregar_documento(
                input_dto.caminho_arquivo
            )

            # Etapa 2: Extrair texto
            self._notificar_progresso(
                "extracao", 10, "Extraindo texto..."
            )
            if modo_proc == "texto_completo":
                await self._extrair_texto_completo(texto)
                self._notificar_progresso(
                    "extracao", 15,
                    f"Texto extraído: {len(texto.secoes)} bloco(s) | modo: texto completo",
                )
            else:
                await self._extrair_secoes(texto)
                self._notificar_progresso(
                    "extracao", 15,
                    f"Texto extraído: {len(texto.secoes)} seção(ões) | modo: por seção",
                )

            # Etapa 3: Revisões por fase (cada agente revisor)
            total_fases = len(self._ucs_revisar)
            for fase_idx, uc_revisar in enumerate(self._ucs_revisar, 1):
                nome_fase = uc_revisar._agente.obter_nome()
                # Traduzir nome para exibição
                nomes_amigaveis = {
                    "revisor_revisao_gramatical": "Revisão Gramatical",
                    "revisor_revisao_tecnica": "Revisão Técnica",
                    "revisor_revisao_estrutural": "Revisão Estrutural",
                }
                nome_exibicao = nomes_amigaveis.get(
                    nome_fase, nome_fase
                )

                pct_inicio = 15 + int(
                    ((fase_idx - 1) / total_fases) * 40
                )
                self._notificar_progresso(
                    "revisao",
                    pct_inicio,
                    f"━━━ INÍCIO: {nome_exibicao}{mock_label}",
                )

                total = len(texto.secoes)
                for i, secao in enumerate(texto.secoes, 1):
                    pct = pct_inicio + int(
                        (i / total) * (40 / total_fases)
                    )
                    self._notificar_progresso(
                        "revisao",
                        pct,
                        f"  [{nome_exibicao}] Seção {i}/{total}: "
                        f"{secao.titulo}",
                    )
                    await uc_revisar.executar(secao, texto)

                self._notificar_progresso(
                    "revisao",
                    pct_inicio + int(40 / total_fases),
                    f"━━━ FIM: {nome_exibicao}",
                )

            # Etapa 4: Validação
            self._notificar_progresso(
                "validacao",
                60,
                f"━━━ INÍCIO: Validação{mock_label}",
            )
            for i, secao in enumerate(texto.secoes, 1):
                self._notificar_progresso(
                    "validacao",
                    60 + int((i / len(texto.secoes)) * 10),
                    f"  [Validação] Seção {i}/{len(texto.secoes)}: "
                    f"{secao.titulo}",
                )
                ultima_rev = secao.obter_ultima_revisao()
                config_val = {
                    "texto_original": secao.conteudo_original,
                    "texto_revisado": (
                        ultima_rev.texto_saida
                        if ultima_rev else secao.conteudo_original
                    ),
                    "erros_encontrados": [
                        {
                            "trecho": e.trecho_original,
                            "sugestao": e.sugestao_correcao,
                        }
                        for e in secao.obter_todos_erros()
                    ],
                }
                await self._agente_validador.processar(
                    secao, config_val
                )
            self._notificar_progresso(
                "validacao", 70,
                f"━━━ FIM: Validação",
            )

            # Etapa 5: Consistência
            self._notificar_progresso(
                "consistencia",
                72,
                f"━━━ INÍCIO: Consistência{mock_label}",
            )
            await self._uc_consistencia.executar(texto)
            self._notificar_progresso(
                "consistencia", 78,
                f"━━━ FIM: Consistência",
            )

            # Etapa 6: Síntese
            self._notificar_progresso(
                "sintese",
                80,
                f"━━━ INÍCIO: Síntese{mock_label}",
            )
            contexto_sintese = {
                "total_secoes": len(texto.secoes),
                "secoes": [
                    {
                        "titulo": s.titulo,
                        "erros": len(s.obter_todos_erros()),
                        "iteracoes": s.total_iteracoes,
                    }
                    for s in texto.secoes
                ],
            }
            await self._agentes_revisores[0].gerar_sintese(
                contexto_sintese
            )
            self._notificar_progresso(
                "sintese", 85,
                f"━━━ FIM: Síntese",
            )

            # Etapa 7: Gerar relatórios
            self._notificar_progresso(
                "relatorio",
                87,
                "Gerando relatórios...",
            )
            relatorios = await self._gerar_relatorios(
                texto, input_dto
            )

            # Salvar texto processado
            texto.atualizar_status(
                StatusTexto.CONCLUIDO
            )
            self._texto_repo.salvar(texto)

            self._notificar_progresso(
                "concluido",
                100,
                "Processamento concluído!",
            )

            return ProcessarTextoOutputDTO(
                texto=texto,
                relatorios=relatorios,
                metricas=self._coletar_metricas(texto),
                sucesso=True,
                mensagem="Processamento concluído",
            )

        except Exception as e:
            self._logger.error(
                f"Erro no processamento: {e}"
            )
            return ProcessarTextoOutputDTO(
                sucesso=False,
                mensagem=str(e),
            )

    async def _carregar_documento(
        self, caminho: str
    ) -> TextoEstruturado:
        """
        Carrega e valida o arquivo de documento.

        Suporta PDF, DOCX, ODT e TEX.

        Args:
            caminho: Caminho do arquivo

        Returns:
            Instância de TextoEstruturado carregada

        Raises:
            TextoInvalidoException: Se inválido
        """
        # Validar documento (usa interface existente por ora)
        valido = await self._pdf_processor.validar_pdf(
            caminho
        )
        if not valido:
            raise TextoInvalidoException(
                f"Documento inválido ou formato "
                f"não suportado: {caminho}"
            )

        # Extrair metadados
        metadados = (
            await self._pdf_processor.extrair_metadados(
                caminho
            )
        )
        nome = Path(caminho).name
        tam = Path(caminho).stat().st_size

        # Criar entidade TextoEstruturado
        texto = TextoEstruturado(
            caminho_arquivo=caminho,
            nome_arquivo=nome,
            metadados=metadados,
            tamanho_bytes=tam,
            numero_paginas=metadados.numero_paginas,
        )
        
        # Injetar info da IA (se disponível no use case)
        # Hack: O usecase tem acesso aos agentes, vamos pegar do primeiro
        if self._agentes_revisores:
            agente = self._agentes_revisores[0]
            if hasattr(agente, "_gateway") and agente._gateway:
                texto.info_ia = agente._gateway.obter_info_modelo()

        # Hash para integridade
        texto.calcular_hash()

        # Validar regras de negócio
        valido_negocio, erros = (
            self._validator.validar(texto)
        )
        if not valido_negocio:
            raise TextoInvalidoException(
                f"Validação falhou: {'; '.join(erros)}"
            )

        texto.atualizar_status(
            StatusTexto.PROCESSANDO
        )

        return texto

    async def _extrair_texto_completo(
        self, texto: TextoEstruturado
    ) -> None:
        """
        Extrai texto completo do documento como uma seção única.

        Args:
            texto: Texto estruturado carregado
        """
        conteudo = (
            await self._pdf_processor.extrair_texto(
                texto.caminho_arquivo
            )
        )

        self._logger.info(
            f"Modo texto completo: {len(conteudo)} caracteres extraídos"
        )

        secao = Secao(
            titulo="Texto Completo",
            conteudo_original=conteudo,
            numero_pagina_inicio=1,
            numero_pagina_fim=texto.numero_paginas,
            nivel_hierarquico=1,
        )
        texto.adicionar_secao(secao)

        texto.atualizar_status(
            StatusTexto.REVISANDO
        )

    async def _extrair_secoes(
        self, texto: TextoEstruturado
    ) -> None:
        """
        Extrai conteúdo e detecta seções no documento.

        Args:
            texto: Texto estruturado carregado
        """
        # Extrair texto completo
        conteudo = (
            await self._pdf_processor.extrair_texto(
                texto.caminho_arquivo
            )
        )

        # Detectar seções
        secoes_det = (
            await self._pdf_processor.detectar_secoes(
                conteudo, texto.numero_paginas
            )
        )

        # Converter para entidades
        titulos_vistos = set()
        for sd in secoes_det:
            titulo = sd.titulo
            original = titulo
            contador = 1
            while titulo in titulos_vistos:
                contador += 1
                titulo = f"{original} ({contador})"
            
            titulos_vistos.add(titulo)

            secao = Secao(
                titulo=titulo,
                conteudo_original=sd.conteudo,
                numero_pagina_inicio=sd.pagina_inicio,
                numero_pagina_fim=sd.pagina_fim,
                nivel_hierarquico=sd.nivel,
            )
            texto.adicionar_secao(secao)

        texto.atualizar_status(
            StatusTexto.REVISANDO
        )

    async def _gerar_relatorios(
        self,
        texto: TextoEstruturado,
        input_dto: ProcessarTextoInputDTO,
    ) -> Dict[str, str]:
        """
        Gera relatórios nos formatos solicitados.

        Args:
            texto: Texto processado
            input_dto: DTO de entrada com formatos

        Returns:
            Mapa formato -> caminho do arquivo
        """
        relatorios: Dict[str, str] = {}
        dir_saida = input_dto.opcoes.get(
            "diretorio_saida", "./output"
        )

        for formato in input_dto.formatos_relatorio:
            try:
                caminho = (
                    await self._uc_relatorio.executar(
                        texto, formato, dir_saida
                    )
                )
                relatorios[formato] = caminho
            except ValueError as e:
                self._logger.warning(
                    f"Formato ignorado: {e}"
                )

        return relatorios

    def _coletar_metricas(
        self, texto: TextoEstruturado
    ) -> Dict[str, Any]:
        """
        Coleta métricas do processamento.

        Args:
            texto: Texto processado

        Returns:
            Dicionário com métricas
        """
        return {
            "total_secoes": len(texto.secoes),
            "total_erros": (
                texto.total_erros_encontrados
            ),
            "progresso": texto.progresso_percentual,
            "status": texto.status.value,
        }

    def _notificar_progresso(
        self,
        etapa: str,
        percentual: float,
        mensagem: str,
    ) -> None:
        """
        Notifica callback de progresso.
        """
        if self._callback_progresso:
            dto = ProgressoDTO(
                etapa=etapa,
                percentual=percentual,
                mensagem=mensagem,
            )
            self._callback_progresso(dto)
