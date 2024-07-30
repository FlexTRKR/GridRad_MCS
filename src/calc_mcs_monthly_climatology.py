"""
Script to calculate climatalogical mean MCS statistics from monthly data.
"""
__author__ = "Zhe.Feng@pnnl.gov"
__date__ = "19-July-2024"

import numpy as np
import yaml
import glob, os, sys
import xarray as xr
import pandas as pd
import time, datetime, calendar, pytz

if __name__ == "__main__":

    config_file = sys.argv[1]

    # Get inputs from configuration file
    stream = open(config_file, 'r')
    config = yaml.full_load(stream)
    monthly_dir = config["output_monthly_dir"]
    climo_dir = config["output_climo_dir"]
    climo_years = config["climo_years"]

    # nyears = len(climo_years)
    rainfiles = []
    statsfiles = []
    for yy in range(len(climo_years)):
        # print(f'{yy}: {climo_years[yy]:.0f}')
        iyear = f'{climo_years[yy]:.0f}'
        rainfiles.extend(sorted(glob.glob(f"{monthly_dir}mcs_rainmap_{iyear}*")))
        statsfiles.extend(sorted(glob.glob(f"{monthly_dir}mcs_statsmap_{iyear}*")))
    print(f"Number of rainmap files: {len(rainfiles)}")
    print(f"Number of statsmap files: {len(rainfiles)}")

    os.makedirs(climo_dir, exist_ok=True)

    # Read precip data (for total number of hours in each month only)
    dsp = xr.open_mfdataset(rainfiles, concat_dim='time', combine='nested')
    nhours = dsp.ntimes

    # Read stats data
    ds = xr.open_mfdataset(statsfiles, concat_dim='time', combine='nested')
    nx = ds.sizes['lon']
    ny = ds.sizes['lat']
    lon = ds.lon
    lat = ds.lat

    # Get number of seasons/years
    years = pd.date_range(start=ds.time.min().values, end=ds.time.max().values, freq='AS')
    nyears = len(years)

    # Get min/max year and create output file names
    min_year = ds.time.min().dt.strftime("%Y").values
    max_year = ds.time.max().dt.strftime("%Y").values
    # outfile_season = f'{climo_dir}mcs_statsmap_seasonal_mean_{min_year}_{max_year}.nc'
    outfile_month = f'{climo_dir}mcs_statsmap_monthly_mean_{min_year}_{max_year}.nc'

    #--------------------------------------------------------------
    # Precipitation climo
    #--------------------------------------------------------------
    # Calculate total number of hours each month
    nhours_month = nhours.groupby('time.month').sum(dim='time')

    totpcp_month = 24 * dsp.precipitation.groupby('time.month').sum(dim='time') / nhours_month
    mcspcp_month = 24 * dsp.mcs_precipitation.groupby('time.month').sum(dim='time') / nhours_month
    mcsfrac_month = 100 * mcspcp_month / totpcp_month

    mcspcpfreq_month = 100 * dsp.mcs_precipitation_count.groupby('time.month').sum(dim='time') / nhours_month

    # Number of hours for MCS precipitation
    mcspcpcount_month = dsp.mcs_precipitation_count.groupby('time.month').sum(dim='time')
    # Mean MCS precipitation intensity
    mcspcpintensity_month = dsp.mcs_precipitation.groupby('time.month').sum(dim='time') / mcspcpcount_month

    #--------------------------------------------------------------
    # MCS tracks climo
    #--------------------------------------------------------------
    # For number counts, group by month and sum, then divide by total number of years
    mcs_number_ccs_month = ds.mcs_number_ccs.groupby('time.month').sum(dim='time').load() / nyears
    mcs_number_pf_month = ds.mcs_number_pf.groupby('time.month').sum(dim='time').load() / nyears
    mcs_initccs_month = ds.initiation_ccs.groupby('time.month').sum(dim='time').load() / nyears

    # Calculate number of hours for MCS PF over each pixel
    mcs_nhour_pf_month = ds.mcs_nhour_pf.groupby('time.month').sum(dim='time')
    mcs_nhour_ccs_month = ds.mcs_nhour_ccs.groupby('time.month').sum(dim='time')

    # MCS frequency
    mcs_freq_ccs_month = 100. * mcs_nhour_ccs_month / nhours_month
    mcs_freq_pf_month = 100. * mcs_nhour_pf_month / nhours_month

    # MCS size
    mcs_pfarea_avg_month = (ds.pf_area_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month
    mcs_pfdiam_avg_month = 2 * np.sqrt(mcs_pfarea_avg_month / np.pi)
    
    # MCS lifetime
    mcs_lifetime_avg_month = (ds.lifetime_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month

    # Precipitation metrics
    totalrain_avg_month = (ds.totalrain_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month
    totalrainheavy_avg_month = (ds.totalrainheavy_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month
    rainrateheavy_avg_month = (ds.rainrateheavy_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month
    rainratemax_avg_month = (ds.rainratemax_mean * ds.mcs_nhour_pf).groupby('time.month').sum(dim='time') / mcs_nhour_pf_month

    # Propagation Speed
    nhour_pfspeed_mcs_month = ds.mcs_nhour_speedmcs.groupby('time.month').sum(dim='time')
    pfspeed_mcs_avg_month = (ds.pf_speed_mcs * ds.mcs_nhour_speedmcs).groupby('time.month').sum(dim='time') / nhour_pfspeed_mcs_month
    pfuspeed_mcs_avg_month = (ds.pf_uspeed_mcs * ds.mcs_nhour_speedmcs).groupby('time.month').sum(dim='time') / nhour_pfspeed_mcs_month
    pfvspeed_mcs_avg_month = (ds.pf_vspeed_mcs * ds.mcs_nhour_speedmcs).groupby('time.month').sum(dim='time') / nhour_pfspeed_mcs_month

    # Radar PF metrics
    cc_rain_avg_month = 24 * ds.cc_rain_sl3d.groupby('time.month').sum(dim='time') / nhours_month
    sf_rain_avg_month = 24 * ds.sf_rain_sl3d.groupby('time.month').sum(dim='time') / nhours_month
    cc_dbz20_avg_month = ds.cc_dbz20_mean.groupby('time.month').mean(dim='time')
    core_area_avg_month = ds.core_area_mean.groupby('time.month').mean(dim='time')
    core_majoraxislength_avg_month = ds.core_majoraxislength_mean.groupby('time.month').mean(dim='time')

    #---------------------------------------------------------------------------------
    # Write output to file
    #---------------------------------------------------------------------------------
    dims3d = ['month', 'lat', 'lon']
    var_dict = {
        # Tracks 
        'mcs_number': (dims3d, mcs_number_pf_month.data),
        'mcs_number_ccs': (dims3d, mcs_number_ccs_month.data),
        'mcs_initiation_ccs': (dims3d, mcs_initccs_month.data),
        'mcs_freq_ccs': (dims3d, mcs_freq_ccs_month.data),
        'mcs_freq_pf': (dims3d, mcs_freq_pf_month.data),
        'mcs_pfarea': (dims3d, mcs_pfarea_avg_month.data),
        'mcs_pfdiameter': (dims3d, mcs_pfdiam_avg_month.data),
        'mcs_lifetime': (dims3d, mcs_lifetime_avg_month.data),
        'mcs_totalrain': (dims3d, totalrain_avg_month.data),
        'mcs_totalrainheavy': (dims3d, totalrainheavy_avg_month.data),
        'mcs_rainrateheavy': (dims3d, rainrateheavy_avg_month.data),
        'mcs_rainratemax': (dims3d, rainratemax_avg_month.data),
        'mcs_speed': (dims3d, pfspeed_mcs_avg_month.data),
        'mcs_uspeed': (dims3d, pfuspeed_mcs_avg_month.data),
        'mcs_vspeed': (dims3d, pfvspeed_mcs_avg_month.data),
        # Radar
        'mcs_convective_rain': (dims3d, cc_rain_avg_month.data),
        'mcs_stratiform_rain': (dims3d, sf_rain_avg_month.data),
        'mcs_core_20dbz_echotop': (dims3d, cc_dbz20_avg_month.data),
        'mcs_core_area': (dims3d, core_area_avg_month.data),
        'mcs_core_majoraxislength': (dims3d, core_majoraxislength_avg_month.data),
        # Precipitation
        'precipitation': (dims3d, totpcp_month.data),
        'mcs_precipitation': (dims3d, mcspcp_month.data),
        'mcs_precipitation_frac': (dims3d, mcsfrac_month.data),
        'mcs_precipitation_freq': (dims3d, mcspcpfreq_month.data),
        'mcs_precipitation_intensity': (dims3d, mcspcpintensity_month.data),
        }
    coords_dict = {
        'month': (['month'], totpcp_month.month.data),
        'lat': (['lat'], lat.data),
        'lon': (['lon'], lon.data),
    }
    gattrs_dict = {
        'title': 'MCS precipitation climatology',
        'climo_years': climo_years,
        'contact':'Zhe Feng, zhe.feng@pnnl.gov',
        'created_on':time.ctime(time.time()),
    }
    # Make output Dataset
    dsmap = xr.Dataset(var_dict, coords=coords_dict, attrs=gattrs_dict)

    # Coordinates
    dsmap.month.attrs['long_name'] = 'month'
    dsmap.month.attrs['units'] = 'month'
    dsmap.lon.attrs['long_name'] = 'Longitude'
    dsmap.lon.attrs['units'] = 'degree'
    dsmap.lat.attrs['long_name'] = 'Latitude'
    dsmap.lat.attrs['units'] = 'degree'
    # Precipitation
    dsmap.precipitation.attrs['long_name'] = 'Total precipitation'
    dsmap.precipitation.attrs['units'] = 'mm/day'
    dsmap.mcs_precipitation.attrs['long_name'] = 'MCS precipitation'
    dsmap.mcs_precipitation.attrs['units'] = 'mm/day'
    dsmap.mcs_precipitation_frac.attrs['long_name'] = 'MCS precipitation fraction'
    dsmap.mcs_precipitation_frac.attrs['units'] = '%'
    dsmap.mcs_precipitation_freq.attrs['long_name'] = 'MCS precipitation frequency'
    dsmap.mcs_precipitation_freq.attrs['units'] = '%'
    dsmap.mcs_precipitation_intensity.attrs['long_name'] = 'MCS precipitation intensity'
    dsmap.mcs_precipitation_intensity.attrs['units'] = 'mm/hour'
    # Tracks metrics
    dsmap.mcs_number.attrs['long_name'] = 'Number of MCS (defined by PF)'
    dsmap.mcs_number.attrs['units'] = 'count'
    dsmap.mcs_number_ccs.attrs['long_name'] = 'Number of MCS (defined by CCS)'
    dsmap.mcs_number_ccs.attrs['units'] = 'count'
    dsmap.mcs_freq_ccs.attrs['long_name'] = 'MCS frequency (defined by CCS)'
    dsmap.mcs_freq_ccs.attrs['units'] = '%'
    dsmap.mcs_freq_pf.attrs['long_name'] = 'MCS frequency (defined by PF)'
    dsmap.mcs_freq_pf.attrs['units'] = '%'
    dsmap.mcs_initiation_ccs.attrs['long_name'] = 'MCS initiation count'
    dsmap.mcs_initiation_ccs.attrs['units'] = 'count'
    dsmap.mcs_pfarea.attrs['long_name'] = 'MCS precipitation feature area'
    dsmap.mcs_pfarea.attrs['units'] = 'km2'
    dsmap.mcs_pfdiameter.attrs['long_name'] = 'MCS precipitation feature equivalent diameter'
    dsmap.mcs_pfdiameter.attrs['units'] = 'km'
    dsmap.mcs_lifetime.attrs['long_name'] = 'MCS lifetime'
    dsmap.mcs_lifetime.attrs['units'] = 'hour'
    dsmap.mcs_totalrain.attrs['long_name'] = 'MCS total precipitation'
    dsmap.mcs_totalrain.attrs['units'] = 'mm'
    dsmap.mcs_totalrainheavy.attrs['long_name'] = 'MCS total heavy precipitation (rain rate > 10 mm/h)'
    dsmap.mcs_totalrainheavy.attrs['units'] = 'mm'
    dsmap.mcs_rainrateheavy.attrs['long_name'] = 'MCS heavy rain rate (rain rate > 10 mm/h) mean'
    dsmap.mcs_rainrateheavy.attrs['units'] = 'mm/h'
    dsmap.mcs_rainratemax.attrs['long_name'] = 'MCS max rain rate'
    dsmap.mcs_rainratemax.attrs['units'] = 'mm/h'
    dsmap.mcs_speed.attrs['long_name'] = 'MCS precipitation feature propagation speed'
    dsmap.mcs_speed.attrs['units'] = 'm/s'
    dsmap.mcs_uspeed.attrs['long_name'] = 'MCS precipitation feature propagation speed (zonal direction)'
    dsmap.mcs_uspeed.attrs['units'] = 'm/s'
    dsmap.mcs_vspeed.attrs['long_name'] = 'MCS precipitation feature propagation speed (meridional direction)'
    dsmap.mcs_vspeed.attrs['units'] = 'm/s'
    # Radar
    dsmap.mcs_convective_rain.attrs['long_name'] = 'MCS convective precipitation'
    dsmap.mcs_convective_rain.attrs['units'] = 'mm/day'
    dsmap.mcs_stratiform_rain.attrs['long_name'] = 'MCS stratiform precipitation'
    dsmap.mcs_stratiform_rain.attrs['units'] = 'mm/day'
    dsmap.mcs_core_20dbz_echotop.attrs['long_name'] = 'MCS convective feature 20dBZ echo-top height'
    dsmap.mcs_core_20dbz_echotop.attrs['units'] = 'km'
    dsmap.mcs_core_area.attrs['long_name'] = 'MCS convective feature area'
    dsmap.mcs_core_area.attrs['units'] = 'km^2'
    dsmap.mcs_core_majoraxislength.attrs['long_name'] = 'MCS convective feature major axis length'
    dsmap.mcs_core_majoraxislength.attrs['units'] = 'km'


    fillvalue = np.nan
    # Set encoding/compression for all variables
    comp = dict(zlib=True, _FillValue=fillvalue, dtype='float32')
    encoding = {var: comp for var in dsmap.data_vars}

    dsmap.to_netcdf(path=outfile_month, mode='w', format='NETCDF4', encoding=encoding)
    print(f'Output saved as: {outfile_month}')
    # import pdb; pdb.set_trace()