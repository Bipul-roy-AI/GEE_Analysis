"""Small, local time-series methods with explicit statistical assumptions."""
import numpy as np
from scipy import stats


def standardized_monthly_anomaly(values, dates, baseline_start=2001, baseline_end=2020):
    """Same-calendar-month z score, not gamma-fitted SPI or SPEI.

    Requires at least 10 valid baseline observations for each month. NaNs remain
    missing. Dates must align with values; missing months must not be filled by 0.
    """
    import pandas as pd
    x=np.asarray(values,dtype=float)
    d=pd.DatetimeIndex(dates)
    if len(x)!=len(d):raise ValueError('Date/value length mismatch')
    if d.to_period('M').has_duplicates:raise ValueError('Monthly observations must be unique')
    out=np.full(x.shape,np.nan)
    for month in range(1,13):
        ref=x[(d.month==month)&(d.year>=baseline_start)&(d.year<=baseline_end)]
        ref=ref[np.isfinite(ref)]
        if len(ref)>=10 and ref.std(ddof=1)>0:
            use=d.month==month
            out[use]=(x[use]-ref.mean())/ref.std(ddof=1)
    return out


def sen_trend(years, values):
    """Theil-Sen slope and 95% interval; Kendall p-value is uncorrected for autocorrelation.

    Use annual/seasonal aggregates and check serial dependence before inference.
    """
    x,y=np.asarray(years,float),np.asarray(values,float)
    mask=np.isfinite(x)&np.isfinite(y);x,y=x[mask],y[mask]
    if len(x)<5 or len(np.unique(x))!=len(x):raise ValueError('Need >=5 unique valid times')
    fit=stats.theilslopes(y,x,.95)
    tau,p=stats.kendalltau(x,y)
    return dict(n=len(x),slope=fit.slope,intercept=fit.intercept,
                slope_low=fit.low_slope,slope_high=fit.high_slope,tau=tau,p_uncorrected=p)


def spell_lengths(exceedances):
    """Consecutive TRUE run lengths; missing data break a run, never bridge it."""
    runs=[];run=0
    for value in exceedances:
        if value is not None and np.isfinite(value) and bool(value):run+=1
        elif run:runs.append(run);run=0
    if run:runs.append(run)
    return runs
