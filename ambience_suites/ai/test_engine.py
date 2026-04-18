# SPDX-License-Identifier: Apache-2.0
"""Unit tests for 1970ai engine prompt feature configuration."""

from __future__ import annotations

import pytest

from ambience_suites.ai.engine import AI1970Engine, EngineConfig, PromptFeature


def test_engine_config_accepts_zero_primary_features() -> None:
    cfg = EngineConfig(
        prompt_features=[
            PromptFeature(
                name="secondary-only",
                source_repository="example/repo",
                prompt_role="additional",
                primary=False,
            )
        ]
    )
    assert len(cfg.prompt_features) == 1


def test_engine_config_accepts_single_primary_feature() -> None:
    cfg = EngineConfig(
        prompt_features=[
            PromptFeature(
                name="primary",
                source_repository="example/repo",
                prompt_role="primary-ui-ux-llm-slm",
                primary=True,
            ),
            PromptFeature(
                name="secondary",
                source_repository="example/repo-2",
                prompt_role="additional",
                primary=False,
            ),
        ]
    )
    engine = AI1970Engine(cfg)
    assert engine.active_prompt_features()[0].primary is True


def test_engine_config_rejects_multiple_primary_features() -> None:
    with pytest.raises(ValueError, match="only one primary feature"):
        EngineConfig(
            prompt_features=[
                PromptFeature(
                    name="primary-a",
                    source_repository="example/repo-a",
                    prompt_role="primary-ui-ux-llm-slm",
                    primary=True,
                ),
                PromptFeature(
                    name="primary-b",
                    source_repository="example/repo-b",
                    prompt_role="primary-ui-ux-llm-slm",
                    primary=True,
                ),
            ]
        )
