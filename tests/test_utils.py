# coding: utf-8
from datetime import datetime, date, timedelta

from mock import patch

from app.config import config
from app.helpers.sundial import Sundial


def test_sundial():

    with patch('app.helpers.sundial.date') as mock_date:
        mock_date.today.return_value = date(2019, 6, 2)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        sundial = Sundial()

        with patch('app.helpers.sundial.datetime') as mock_datetime:
            mock_datetime.now.return_value = sundial.sun['sunrise']
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            assert sundial.is_day() is False
            assert sundial.mode == Sundial.NIGHT

        # DAY mode `DAY_LIGHT_OFFSET` minutes after sunrise.
        with patch('app.helpers.sundial.datetime') as mock_datetime:
            mock_datetime.now.return_value = sundial.sun['sunrise'] \
                + timedelta(minutes=int(config.get('DAY_LIGHT_OFFSET')))
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            assert sundial.is_day() is True
            assert sundial.mode == Sundial.DAY

        # NIGHT mode at sunset
        with patch('app.helpers.sundial.datetime') as mock_datetime:
            mock_datetime.now.return_value = sundial.sun['sunset']
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            assert sundial.is_day() is False
            assert sundial.mode == Sundial.NIGHT

        # NIGHT mode `DAY_LIGHT_OFFSET` minutes before sunset
        with patch('app.helpers.sundial.datetime') as mock_datetime:
            mock_datetime.now.return_value = sundial.sun['sunset'] \
                - timedelta(minutes=int(config.get('DAY_LIGHT_OFFSET')))
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            assert sundial.is_day() is False
            assert sundial.mode == Sundial.NIGHT

        # DAY mode `DAY_LIGHT_OFFSET` minutes and 1 sec. before sunset
        with patch('app.helpers.sundial.datetime') as mock_datetime:
            mock_datetime.now.return_value = sundial.sun['sunset'] \
                - timedelta(minutes=int(config.get('DAY_LIGHT_OFFSET')),
                            seconds=1)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            assert sundial.is_day() is True
            assert sundial.mode == Sundial.DAY

