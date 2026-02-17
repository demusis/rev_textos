
import pytest
from unittest.mock import MagicMock, AsyncMock
import asyncio

from src.application.use_cases.processar_texto.processar_texto_use_case import ProcessarTextoUseCase
from src.application.use_cases.processar_texto.dto import ProcessarTextoInputDTO


def test_cancellation_during_processing():
    async def _run_test():
        # Arrange
        mock_pdf_processor = MagicMock()
        mock_pdf_processor.validar_pdf = AsyncMock(return_value=True)
        mock_pdf_processor.extrair_metadados = AsyncMock(return_value=MagicMock(numero_paginas=1))
        
        # Mock agents
        mock_agent = MagicMock()
        mock_agent.obter_nome.return_value = "mock_agent"
        
        # Mock repository
        mock_repo = MagicMock()
        
        # Mock config
        mock_config = MagicMock()
        mock_config.carregar_configuracao.return_value = {"modo_processamento": "texto_completo"}
        
        # Mock logger
        mock_logger = MagicMock()
        
        # Callback that raises exception on second call (simulating cancel after load)
        cancel_check_mock = MagicMock(side_effect=[None, Exception("Processamento interrompido pelo usuário.")])
        
        use_case = ProcessarTextoUseCase(
            pdf_processor=mock_pdf_processor,
            agentes_revisores=[mock_agent],
            agente_validador=MagicMock(),
            agente_consistencia=MagicMock(),
            texto_repo=mock_repo,
            config_repo=mock_config,
            geradores_relatorio={},
            logger=mock_logger,
            check_cancel=cancel_check_mock
        )
        
        input_dto = ProcessarTextoInputDTO(
            caminho_arquivo="dummy.pdf"
        )


        # Act
        result = await use_case.executar(input_dto)
        return result, cancel_check_mock

    # Run async test synchronously
    result, cancel_check_mock = asyncio.run(_run_test())

    # Assert
    assert result.sucesso is False
    assert "Processamento interrompido pelo usuário" in result.mensagem
    # Verify that check_cancel was called
    assert cancel_check_mock.call_count >= 2
