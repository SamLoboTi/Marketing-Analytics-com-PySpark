"""Fixtures compartilhadas pelos testes do pipeline."""

import pytest

from main import criar_spark


@pytest.fixture(scope="session")
def spark():
    """Disponibiliza uma unica sessao Spark para toda a suite."""
    session = criar_spark()
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
