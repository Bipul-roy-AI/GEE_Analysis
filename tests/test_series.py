import numpy as np
import pandas as pd
import pytest
from bdgee.series import sen_trend, standardized_monthly_anomaly, spell_lengths


def test_sen_slope_robust_to_outlier_and_missing_year():
    years=np.arange(2001,2021)
    y=2*(years-2001)+5.0
    y[5]=1000;y[9]=np.nan
    result=sen_trend(years,y)
    assert result['n']==19
    assert result['slope']==pytest.approx(2)
    assert result['slope_low']<=2<=result['slope_high']


def test_seasonal_anomaly_is_not_biased_by_monthly_cycle():
    d=pd.date_range('2001-01-01','2021-12-01',freq='MS')
    x=100*d.month.to_numpy()+d.year.to_numpy()-2001
    z=standardized_monthly_anomaly(x,d)
    assert z[-1]==pytest.approx(z[-12])
    assert np.isfinite(z).all()
    assert np.mean(z[:240])==pytest.approx(0,abs=1e-10)


def test_missing_data_break_spell():
    assert spell_lengths([1,1,np.nan,1,0,1,1,1])==[2,1,3]
    assert spell_lengths([])==[]


def test_degenerate_series_rejected():
    with pytest.raises(ValueError):sen_trend([1,1,2,3,4],[1,2,3,4,5])
    d=pd.date_range('2001-01-01',periods=240,freq='MS')
    assert np.isnan(standardized_monthly_anomaly(np.ones(240),d)).all()
