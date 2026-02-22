import pandas as pd
import numpy as np
import streamlit as st
import os

@st.cache_data
def load_and_clean_data(app_path="application_data.csv", prev_app_path="previous_application.csv"):
    try:
        # Load data (Pandas read_csv inherently supports HTTP URLs)
        app = pd.read_csv(app_path)
        prev_app = pd.read_csv(prev_app_path)
    except Exception as e:
        print(f"Error loading datasets from {app_path} or {prev_app_path}: {e}")
        return None, None, None

    # Clean app data
    msng_info = pd.DataFrame(app.isnull().sum().sort_values()).reset_index()
    msng_info.rename(columns={'index': 'col_name', 0: 'null_count'}, inplace=True)
    msng_info['msng_pct'] = msng_info['null_count'] / app.shape[0] * 100
    
    # Drop columns with >40% missing values
    msng_col = msng_info[msng_info['msng_pct'] >= 40]['col_name'].to_list()
    app_msng_rmvd = app.drop(labels=msng_col, axis=1)

    # Impute application missing values
    app_cleaned = app_msng_rmvd.copy()
    if 'CNT_FAM_MEMBERS' in app_cleaned.columns:
        app_cleaned['CNT_FAM_MEMBERS'] = app_cleaned['CNT_FAM_MEMBERS'].fillna(app_cleaned['CNT_FAM_MEMBERS'].mode()[0])
    if 'OCCUPATION_TYPE' in app_cleaned.columns:
        app_cleaned['OCCUPATION_TYPE'] = app_cleaned['OCCUPATION_TYPE'].fillna(app_cleaned['OCCUPATION_TYPE'].mode()[0])
    if 'NAME_TYPE_SUITE' in app_cleaned.columns:
        app_cleaned['NAME_TYPE_SUITE'] = app_cleaned['NAME_TYPE_SUITE'].fillna(app_cleaned['NAME_TYPE_SUITE'].mode()[0])
    if 'AMT_ANNUITY' in app_cleaned.columns:
        app_cleaned['AMT_ANNUITY'] = app_cleaned['AMT_ANNUITY'].fillna(app_cleaned['AMT_ANNUITY'].mean())
    if 'AMT_GOODS_PRICE' in app_cleaned.columns:
        app_cleaned['AMT_GOODS_PRICE'] = app_cleaned['AMT_GOODS_PRICE'].fillna(app_cleaned['AMT_GOODS_PRICE'].median())

    # Convert negative days to positive
    days_cols = [col for col in app_cleaned.columns if col.startswith("DAYS")]
    for col in days_cols:
        app_cleaned[col] = abs(app_cleaned[col])

    # Feature Engineering (Ranges) in app
    if 'AMT_GOODS_PRICE' in app_cleaned.columns:
        bins = [0, 100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, np.inf]
        ranges = ['0-100K','100k-200K','200K-300K','300K-400K','400K-500K','500K-600K','600K-700K','700K-800K','800K-900K','Above 900K']
        app_cleaned['AMT_GOODS_PRICE_RANGE'] = pd.cut(app_cleaned['AMT_GOODS_PRICE'], bins, labels=ranges)

    if 'AMT_INCOME_TOTAL' in app_cleaned.columns:
        bins = [0, 100000, 150000, 200000, 250000, 300000, 350000, 400000, np.inf]
        ranges = ['0-100K','100K-150K','150K-200K','200K-250K','250K-300K','300K-350K','350K-400K','Above 400K']
        app_cleaned['AMT_INCOME_TOTAL_RANGE'] = pd.cut(app_cleaned['AMT_INCOME_TOTAL'], bins, labels=ranges)

    if 'AMT_CREDIT' in app_cleaned.columns:
        bins = [0, 200000, 400000, 600000, 800000, 900000, 1000000, 2000000, 3000000, np.inf]
        ranges = ['0-200K','200K-400K','400K-600K','600K-800K','800K-900K','900K-1M','1M-2M','2M-3M','Above 3M']
        app_cleaned['AMT_CREDIT_RANGE'] = pd.cut(app_cleaned['AMT_CREDIT'], bins, labels=ranges)

    # Clean prev app data
    null_count = pd.DataFrame(prev_app.isnull().sum().sort_values(ascending=False)/prev_app.shape[0]*100).reset_index().rename(columns={'index':'var', 0:'count_pct'})
    var_msng_ge_40 = list(null_count[null_count['count_pct'] >= 40]['var'])
    nva_cols = var_msng_ge_40 + ['WEEKDAY_APPR_PROCESS_START','HOUR_APPR_PROCESS_START','FLAG_LAST_APPL_PER_CONTRACT','NFLAG_LAST_APPL_IN_DAY']
    # Keep only columns that exist before dropping
    nva_cols = [c for c in nva_cols if c in prev_app.columns]
    prev_app_cleaned = prev_app.drop(labels=nva_cols, axis=1)

    # Impute prev app missing values
    if 'AMT_GOODS_PRICE' in prev_app_cleaned.columns:
        prev_app_cleaned['AMT_GOODS_PRICE'] = prev_app_cleaned['AMT_GOODS_PRICE'].fillna(prev_app_cleaned['AMT_GOODS_PRICE'].median())
    if 'AMT_ANNUITY' in prev_app_cleaned.columns:
        prev_app_cleaned['AMT_ANNUITY'] = prev_app_cleaned['AMT_ANNUITY'].fillna(prev_app_cleaned['AMT_ANNUITY'].median())
    if 'PRODUCT_COMBINATION' in prev_app_cleaned.columns:
        prev_app_cleaned['PRODUCT_COMBINATION'] = prev_app_cleaned['PRODUCT_COMBINATION'].fillna(prev_app_cleaned['PRODUCT_COMBINATION'].mode()[0])
    if 'CNT_PAYMENT' in prev_app_cleaned.columns:
        prev_app_cleaned['CNT_PAYMENT'] = prev_app_cleaned['CNT_PAYMENT'].fillna(0)

    # Merge dataset
    merged_df = pd.merge(app_cleaned, prev_app_cleaned, how='inner', on='SK_ID_CURR')
    
    return app_cleaned, prev_app_cleaned, merged_df

