import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from src.application.use_cases.processar_texto.processar_texto_use_case import ProcessarTextoUseCase
from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.entities.secao import Secao

def test_log_formato_com_pagina():
    async def run_test():
        # Mocks
        pdf_processor = MagicMock()
        agente_revisor = MagicMock()
        agente_consistencia = MagicMock()
        texto_repo = MagicMock()
        config_repo = MagicMock()
        geradores = {}
        logger = MagicMock()
        callback_progresso = MagicMock()

        # Use Case
        use_case = ProcessarTextoUseCase(
            pdf_processor, agente_revisor, agente_consistencia,
            texto_repo, config_repo, geradores, logger,
            callback_progresso=callback_progresso
        )

        # Setup Texto and Secao
        texto = MagicMock(spec=TextoEstruturado)
        secao = Secao(
            titulo="Teste Titulo",
            conteudo_original="Conteudo",
            numero_pagina_inicio=5,
            numero_pagina_fim=7
        )
        texto.secoes = [secao]

        # Mock _uc_revisar
        use_case._uc_revisar = AsyncMock()
        use_case._uc_revisar.executar.return_value = None

        # Execute _revisar_secoes directly
        await use_case._revisar_secoes(texto)

        # Verify callback
        assert callback_progresso.called
        # The callback is called once per section with a ProgressoDTO
        # arguments: callback_progresso(ProgressoDTO(...))
        # call_args[0] is the tuple of args, so call_args[0][0] is the DTO
        dto = callback_progresso.call_args[0][0]
        
        expected_msg = "Revisando seção 1/1: Teste Titulo (Pág. 5)"
        print(f"Mensagem recebida: {dto.mensagem}")
        assert expected_msg in dto.mensagem

    asyncio.run(run_test())
