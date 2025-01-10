## 2025/1/20 Update to Provide Multi-Languages

from models.util import convert_path_os
import streamlit as st
import subprocess
import pandas as pd
import pickle
import platform
from link_performance import sp_link_performance

# 定义多语言文本
LANGUAGES = {
    "en": {
        "title": "Satlink",
        "sidebar_title": "Satlink",
        "sidebar_description": "SatLink is a python based application that runs specific satellite downlink calculations.",
        "sidebar_teaching": "This project is an attempt to simplify satellite's link budget calculations and to create a tool for teaching purposes.",
        "github_link": "Please refer to [**github**](https://github.com/cfragoas/SatLink) for more information",
        "ground_station": "Ground Station",
        "latitude": "Latitude (degrees)",
        "longitude": "Longitude (degrees)",
        "satellite": "Satellite",
        "sat_longitude": "Longitude (degrees)",
        "max_bandwidth": "Transponder's max bandwidth (MHz)",
        "altitude": "Altitude (Km)",
        "effective_bandwidth": "Effective bandwidth (MHz)",
        "frequency": "Frequency (GHz)",
        "roll_off": "Roll-off",
        "eirp": "EIRP (dBW)",
        "modulation": "Modulation",
        "polarization": "Polarization",
        "reception": "Reception Characteristics",
        "antenna_size": "Antenna Size (m)",
        "antenna_efficiency": "Antenna Efficiency",
        "lnb_gain": "LNB Gain (dB)",
        "lnb_temp": "LNB Noise Temp. (K)",
        "cable_loss": "Cable Loss (dB)",
        "additional_losses": "Additional Losses (dB)",
        "max_depoint": "Maximum depointing (degrees)",
        "run_calculations": "Run Calculations",
    },
    "zh": {
        "title": "Satlink",
        "sidebar_title": "Satlink",
        "sidebar_description": "SatLink 是一个基于 Python 的应用程序，用于执行特定的卫星下行链路计算。",
        "sidebar_teaching": "该项目旨在简化卫星链路预算计算，并创建一个用于教学目的的工具。",
        "github_link": "请参考 [**github**](https://github.com/cfragoas/SatLink) 获取更多信息",
        "ground_station": "地面站",
        "latitude": "纬度 (度)",
        "longitude": "经度 (度)",
        "satellite": "卫星",
        "sat_longitude": "经度 (度)",
        "max_bandwidth": "转发器最大带宽 (MHz)",
        "altitude": "高度 (Km)",
        "effective_bandwidth": "有效带宽 (MHz)",
        "frequency": "频率 (GHz)",
        "roll_off": "滚降系数",
        "eirp": "等效全向辐射功率 (dBW)",
        "modulation": "调制方式",
        "polarization": "极化方式",
        "reception": "接收特性",
        "antenna_size": "天线尺寸 (米)",
        "antenna_efficiency": "天线效率",
        "lnb_gain": "LNB 增益 (dB)",
        "lnb_temp": "LNB 噪声温度 (K)",
        "cable_loss": "电缆损耗 (dB)",
        "additional_losses": "附加损耗 (dB)",
        "max_depoint": "最大偏离角度 (度)",
        "run_calculations": "运行计算",
    },
}

# 确保 st.set_page_config() 是第一个 Streamlit 命令
st.set_page_config(page_title="Satlink", page_icon='UI\icon.png', layout="wide", initial_sidebar_state="auto", menu_items=None)

# 在侧边栏中添加语言选择器
language = st.sidebar.selectbox("Language", options=list(LANGUAGES.keys()), format_func=lambda x: "English" if x == "en" else "中文")

# 使用多语言文本
st.sidebar.title(LANGUAGES[language]["sidebar_title"])
st.sidebar.image('pics/LogoSatLink225_225_white.png', width=150)
st.sidebar.subheader(LANGUAGES[language]["sidebar_description"])
st.sidebar.subheader(LANGUAGES[language]["sidebar_teaching"])
st.sidebar.markdown(LANGUAGES[language]["github_link"])

# 地面站参数
st.subheader(LANGUAGES[language]["ground_station"])
grstat_exp = st.expander(label='', expanded=True)
with grstat_exp:
    grstat_col1, grstat_col2 = st.columns(2)
    site_lat = grstat_col1.number_input(LANGUAGES[language]["latitude"], key="latitude")
    site_long = grstat_col2.number_input(LANGUAGES[language]["longitude"], key="longitude")

# 卫星参数
st.subheader(LANGUAGES[language]["satellite"])
sat_exp = st.expander(label='', expanded=True)
path = convert_path_os('models\\Modulation_dB.csv')
mod_list = pd.read_csv(path, sep=';')['Modcod']

with sat_exp:
    sat_col1, sat_col2, sat_col3, sat_col4, sat_col5 = st.columns(5)
    sat_long = sat_col1.number_input(LANGUAGES[language]["sat_longitude"], key="sat_longitude")
    max_bw = sat_col1.number_input(LANGUAGES[language]["max_bandwidth"], key="max_bandwidth")
    sat_height = sat_col2.number_input(LANGUAGES[language]["altitude"], key="altitude")
    bw_util = sat_col2.number_input(LANGUAGES[language]["effective_bandwidth"], key="effective_bandwidth")
    freq = sat_col3.number_input(LANGUAGES[language]["frequency"], key="frequency")
    roll_off = sat_col3.number_input(LANGUAGES[language]["roll_off"], key="roll_off")
    max_eirp = sat_col4.number_input(LANGUAGES[language]["eirp"], key="eirp")
    modcod = sat_col4.selectbox(LANGUAGES[language]["modulation"], mod_list, key="modulation")
    pol = sat_col5.selectbox(LANGUAGES[language]["polarization"], ('Horizontal', 'Vertical', 'Circular'), key="polarization")

# 接收参数
st.subheader(LANGUAGES[language]["reception"])
rcp_exp = st.expander(label='', expanded=True)
with rcp_exp:
    rcp_col1, rcp_col2, rcp_col3, rcp_col4 = st.columns(4)
    ant_size = rcp_col1.number_input(LANGUAGES[language]["antenna_size"], key="antenna_size")
    ant_eff = rcp_col1.number_input(LANGUAGES[language]["antenna_efficiency"], key="antenna_efficiency")
    lnb_gain = rcp_col2.number_input(LANGUAGES[language]["lnb_gain"], key="lnb_gain")
    lnb_temp = rcp_col2.number_input(LANGUAGES[language]["lnb_temp"], key="lnb_temp")
    cable_loss = rcp_col3.number_input(LANGUAGES[language]["cable_loss"], key="cable_loss")
    aditional_losses = rcp_col3.number_input(LANGUAGES[language]["additional_losses"], key="additional_losses")
    max_depoint = rcp_col4.number_input(LANGUAGES[language]["max_depoint"], key="max_depoint")

# 运行计算按钮
db_field = st.button(LANGUAGES[language]["run_calculations"], key="run_calculations")
if db_field:
    path = convert_path_os('temp\\args.pkl')
    with open(path, 'wb') as f:
        pickle.dump(
            [site_lat, site_long, sat_long, freq, max_eirp, sat_height, max_bw, bw_util,
                modcod, pol, roll_off, ant_size, ant_eff, lnb_gain, lnb_temp, aditional_losses,
                cable_loss, max_depoint, 1, 0], f)
        f.close()

    sp_link_performance()
    path = convert_path_os('temp\\out.txt')
    with open(path, 'r') as output:
        x = output.read()

    st.text(x)
