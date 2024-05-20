from test.config.data import sigils, uniques
from typing import Any

import pytest
from pydantic import ValidationError

from config.models import ProfileModel


class TestSigil:
    @pytest.fixture(autouse=True)
    def setup(self, mock_ini_loader):
        self.mock_ini_loader = mock_ini_loader

    @pytest.mark.parametrize("data", sigils.all_bad_cases)
    def test_all_bad_cases(self, data: dict[str, Any]):
        with pytest.raises(ValidationError):
            data["name"] = "bad"
            ProfileModel(**data)

    @pytest.mark.parametrize("data", sigils.all_good_cases)
    def test_all_good_cases(self, data: dict[str, Any]):
        data["name"] = "good"
        assert ProfileModel(**data)


class TestUnique:
    @pytest.fixture(autouse=True)
    def setup(self, mock_ini_loader):
        self.mock_ini_loader = mock_ini_loader

    @pytest.mark.parametrize("data", uniques.all_bad_cases)
    def test_all_bad_cases(self, data: dict[str, Any]):
        with pytest.raises(ValidationError):
            data["name"] = "bad"
            ProfileModel(**data)

    def test_all_good_cases(self):
        assert ProfileModel(**uniques.all_good_cases)
