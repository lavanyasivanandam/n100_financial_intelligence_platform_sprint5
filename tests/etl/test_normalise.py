import pytest
from src.etl.normalizer import normalize_year,normalize_ticker

@pytest.mark.parametrize('raw,expected',[('Mar-23', '2023-03'), ('Mar-13', '2013-03'), ('Dec 2012', '2012-12'), ('Dec-22', '2022-12'), ('FY24', '2024-03'), ('FY2024', '2024-03'), ('2024', '2024-03'), ('2024.0', '2024-03'), ('2019-06', '2019-06'), ('Jan-20', '2020-01'), ('Feb-21', '2021-02'), ('Apr-22', '2022-04'), ('May-23', '2023-05'), ('Jun-24', '2024-06'), ('Jul-20', '2020-07'), ('Aug-21', '2021-08'), ('Sep-22', '2022-09'), ('Oct-23', '2023-10'), ('Nov-24', '2024-11'), ('xyz', 'PARSE_ERROR')])
def test_year_cases(raw,expected): assert normalize_year(raw)==expected

@pytest.mark.parametrize('raw,expected',[(' tcs ', 'TCS'), ('tcs', 'TCS'), ('TCS', 'TCS'), (' infy', 'INFY'), ('RELIANCE ', 'RELIANCE'), ('hdfcbank', 'HDFCBANK'), ('HdfcBank', 'HDFCBANK'), ('itc', 'ITC'), (' abb ', 'ABB'), ('L&T', 'L&T'), ('M&M', 'M&M'), ('BAJAJ-AUTO', 'BAJAJ-AUTO'), ('ICICI-BANK', 'ICICI-BANK'), (' SBIN ', 'SBIN'), ('ZOMATO', 'ZOMATO'), ('titan', 'TITAN'), (' axisbank ', 'AXISBANK'), ('adaniports', 'ADANIPORTS'), ('  TCS  ', 'TCS'), ('', '')])
def test_ticker_cases(raw,expected): assert normalize_ticker(raw)==expected
