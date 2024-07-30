# **U.S. MCS Tracking Database Analysis**


---
This repository contains analysis codes and Jupyter Notebooks for the MCS tracking database over the United States. The dataset is available at [Feng (2019)](https://doi.org/10.5439/1571643), a free-to-register account is required at [ARM](https://arm.gov/) (Atmospheric Radiation Measurement User Facility, operated by the U.S. Department of Energy).

## Post-processing Scripts
---

The `/src` directory contains post-processing scripts. 

--

### Remove Tropical Cyclones

These scripts remove MCS tracks near Tropical Cyclones (TCs) using the IBTrACS database [(Knapp et al. 2018)](https://doi.org/10.25921/82ty-9e16). This post-processing has already been applied to the V3 MCS database.

The `${}` are command line inputs, examples:

`${config}: 'config_gridrad_conus.yml'`

`${dates}: '20040101.0000_20050101.0000'`

--

* **Pre-process IBTrACS data:**

`python preprocess_tc_ibtracs.py`

* **Find MCS track numbers near TCs:**

`python find_mcs_tracks_in_tc.py ${dates} ${config}`

* **Remove MCS tracks near TCs:**

`python filter_mcs_tracks_ar_tc.py ${dates} ${config}`

* **Run find MCS track numbers near TCs for each year:**

`bash loop_find_mcs_tracks_tc.sh`

* **Run Remove MCS tracks near TCs for each year:**

`bash loop_filter_mcs_tracks_ar_tc.sh`

--

### Calculate MCS Monthly Statistics

These scripts calculate monthly-mean MCS statistics on the native grid:

The `${}` are command line inputs, examples:

`${config}: 'config_gridrad_conus.yml'`

`${year}: '2004'`

`${month}: '6'`

`${start_date}: '2004-01-01'`

`${end_date}: '2005-01-01'`

--

* **Calculate monthly MCS precipitation:**

`python calc_tbpf_mcs_monthly_rainmap_gridrad.py ${config} ${year} ${month}`

* **Calculate monthly MCS track statistics:**

`python calc_tbpf_mcs_monthly_statsmap_gridrad.py ${config} ${year} ${month}`

* **Make slurm tasks for all months:**

`python make_mcs_monthly_joblib.py ${start_date} ${end_date}`

--

## Analysis Notebooks
---

The `/Notebooks` directory contains Jupyter Notebooks for plotting MCS statistics. 

--

# **References**

---

Feng, Z. (2019). Mesoscale convective system (MCS) database over United States. [Dataset]. Retrieved from: [https://doi.org/10.5439/1571643
](https://doi.org/10.5439/1571643)

Knapp, K. R., Diamond, H. J., Kossin, J. P., Kruk, M. C., & Schreck, C. J. I. (2018). International Best Track Archive for Climate Stewardship (IBTrACS) Project, Version 4. Retrieved from: [https://doi.org/10.25921/82ty-9e16](https://doi.org/10.25921/82ty-9e16)
