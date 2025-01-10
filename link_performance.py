from GrStat import GroundStation, Reception
from sat import Satellite
from models.util import convert_path_os
from pathos.pools import ParallelPool
import pandas as pd
import numpy as np
import pickle
import tqdm
import time
import datetime
import sys, os, platform

# this file contains the functions used to calculate availability and display the results in the interface
# STILL NEED TO CREATE A HEADER IN THE CSV OUTPUT (mp_link_performance)

# 定义多语言文本
LANGUAGES = {
    "en": {
        "results": "RESULTS",
        "link_budget": "Link budget at 0.1%:",
        "c_over_n0": "C/N0: {} dB",
        "snr": "SNR: {} dB",
        "availability": "Actual SNR target's availability: {} %",
        "snr_at_availability": "SNR at Above availability: {} dB",
        "reception_characteristics": "Reception characteristics:",
        "earth_radius": "Earth's radius in lat/long: {} km",
        "elevation_angle": "Elevation angle: {} degrees",
        "link_length": "Link length: {} km",
        "ground_noise_temp": "Ground noise temperature: {} K",
        "sky_brightness_temp": "Sky brightness temperature: {} K",
        "antenna_noise_temp": "Antenna noise temperature: {} K",
        "antenna_noise_rain": "Antenna noise temperature w/ rain: {} K",
        "total_noise_temp": "Total noise temperature: {} K",
        "antenna_gain": "Reception antenna gain: {} dBi",
        "beamwidth": "Reception antenna 3dB beamwidth: {} degrees",
        "figure_of_merit": "Figure of Merit: {}",
        "link_budget_analysis": "Link budget Analysis:",
        "gaseous_attenuation": "Gaseous attenuation: {}",
        "cloud_attenuation": "Cloud attenuation: {}",
        "rain_attenuation": "Rain attenuation: {}",
        "scintillation_attenuation": "Scintillation attenuation: {}",
        "total_atmospheric_attenuation": "Total atmospheric attenuation: {}",
        "free_space_attenuation": "Free space attenuation: {}",
        "total_attenuation": "Free space + atmospheric + depointing attenuation: {} dB",
        "reception_threshold": "Reception threshold (SNR): {} dB",
        "runtime": "Runtime: {} s",
    },
    "zh": {
        "results": "结果",
        "link_budget": "0.1% 的链路预算:",
        "c_over_n0": "C/N0: {} dB",
        "snr": "信噪比 (SNR): {} dB",
        "availability": "实际信噪比目标的可用性: {} %",
        "snr_at_availability": "上述可用性下的信噪比: {} dB",
        "reception_characteristics": "接收特性:",
        "earth_radius": "地球半径 (纬度/经度): {} km",
        "elevation_angle": "仰角: {} 度",
        "link_length": "链路长度: {} km",
        "ground_noise_temp": "地面噪声温度: {} K",
        "sky_brightness_temp": "天空亮度温度: {} K",
        "antenna_noise_temp": "天线噪声温度: {} K",
        "antenna_noise_rain": "带雨的天线噪声温度: {} K",
        "total_noise_temp": "总噪声温度: {} K",
        "antenna_gain": "接收天线增益: {} dBi",
        "beamwidth": "接收天线 3dB 波束宽度: {} 度",
        "figure_of_merit": "品质因数: {}",
        "link_budget_analysis": "链路预算分析:",
        "gaseous_attenuation": "气体衰减: {}",
        "cloud_attenuation": "云衰减: {}",
        "rain_attenuation": "雨衰减: {}",
        "scintillation_attenuation": "闪烁衰减: {}",
        "total_atmospheric_attenuation": "总大气衰减: {}",
        "free_space_attenuation": "自由空间衰减: {}",
        "total_attenuation": "自由空间 + 大气 + 偏离衰减: {} dB",
        "reception_threshold": "接收阈值 (SNR): {} dB",
        "runtime": "运行时间: {} 秒",
    },
}

def point_availability(args):
    point = args[0]
    sat = args[1]
    reception = args[2]
    margin = args[3]
    snr_relaxation = args[4]
    lat = point['Lat']
    long = point['Long']
    station = GroundStation(lat, long)
    sat.set_grstation(station)
    sat.set_reception(reception)
    point['availability'] = sat.get_availability(margin, snr_relaxation)
    return point

def sp_link_performance():
    path = convert_path_os('temp\\args.pkl')
    with open(path, 'rb') as f:
        (site_lat, site_long, sat_long, freq, max_eirp, sat_height, max_bw, bw_util, modcod, pol,
         roll_off, ant_size, ant_eff, lnb_gain, lnb_temp, coupling_loss, cable_loss, max_depoint,
         snr_relaxation, margin, language) = pickle.load(f)
        f.close()

    # 获取当前语言
    lang = LANGUAGES.get(language, LANGUAGES["en"])

    #####################################
    ##### ground station parameters #####
    #####################################

    # creating a ground station object
    station = GroundStation(site_lat, site_long)


    ##############################
    ### satellite parameters ###
    ##############################

    # reading the modulation and fec from the csv file
    path = convert_path_os('models\\Modulation_dB.csv')
    data = pd.read_csv(path, sep=';')
    line = data.loc[(data.Modcod) == modcod]
    mod = line['Modulation'].values[0]
    fec = line['FEC'].values[0]

    # creating the satellite object
    satelite = Satellite(sat_long, freq, max_eirp, sat_height, max_bw, bw_util, 0, 0, mod, roll_off, fec)
    
    # assigning a ground station to the satellite
    satelite.set_grstation(station)

    ##############################
    ### reception parameters ####
    ##############################

    polarization_loss = 3   # polarization loss in dB

    # creating the reception object
    reception = Reception(ant_size, ant_eff, coupling_loss, polarization_loss, lnb_gain, lnb_temp, cable_loss, max_depoint)
  
    # assigning the reception to the satellite link
    satelite.set_reception(reception)

    ###################################
    #########     OUTPUTS     #########
    ###################################

    ############ SNR target's calculation ################    
    path = convert_path_os('temp\\out.txt')
    sys.stdout = open(path, 'w')

    start = time.time()
    print(lang["results"], file=sys.stdout)
    print('', file=sys.stdout)
    print(lang["link_budget"], file=sys.stdout)
    print('', file=sys.stdout)
    print(lang["c_over_n0"].format(satelite.get_c_over_n0(0.1)), file=sys.stdout)
    print(lang["snr"].format(satelite.get_snr(0.1)), file=sys.stdout)
    print('', file=sys.stdout)
    print('', file=sys.stdout)

    availability = satelite.get_availability(0.5, snr_relaxation)
    print(lang["availability"].format(availability), file=sys.stdout)
    print(lang["snr_at_availability"].format(satelite.get_snr(100 - availability)), file=sys.stdout)
    print('', file=sys.stdout)

    print(lang["reception_characteristics"], file=sys.stdout)
    print('', file=sys.stdout)

    print(lang["earth_radius"].format(np.round(satelite.grstation.get_earth_radius(), 3)), file=sys.stdout)
    print(lang["elevation_angle"].format(np.round(satelite.get_elevation(), 3)), file=sys.stdout)
    print(lang["link_length"].format(np.round(satelite.get_distance(), 3)), file=sys.stdout)
    print(lang["ground_noise_temp"].format(np.round(satelite.reception.get_ground_temp(), 3)), file=sys.stdout)
    print(lang["sky_brightness_temp"].format(np.round(satelite.reception.get_brightness_temp(), 3)), file=sys.stdout)
    print(lang["antenna_noise_temp"].format(np.round(satelite.reception.get_antenna_noise_temp(), 3)), file=sys.stdout)
    print(lang["antenna_noise_rain"].format(np.round(satelite.get_antenna_noise_rain(), 3)), file=sys.stdout)
    print(lang["total_noise_temp"].format(np.round(satelite.get_total_noise_temp(), 3)), file=sys.stdout)
    print(lang["antenna_gain"].format(np.round(satelite.reception.get_antenna_gain(), 3)), file=sys.stdout)
    print(lang["beamwidth"].format(np.round(satelite.reception.get_beamwidth(), 3)), file=sys.stdout)
    print(lang["figure_of_merit"].format(np.round(satelite.get_figure_of_merit(), 3)), file=sys.stdout)
    print('', file=sys.stdout)
    print('', file=sys.stdout)

    a_fs, a_dep, a_g, a_c, a_r, a_s, a_t, a_tot = satelite.get_link_attenuation(satelite.p)

    print(lang["link_budget_analysis"], file=sys.stdout)
    print('', file=sys.stdout)

    print(lang["gaseous_attenuation"].format(np.round(a_g, 3)), file=sys.stdout)
    print(lang["cloud_attenuation"].format(np.round(a_c, 3)), file=sys.stdout)
    print(lang["rain_attenuation"].format(np.round(a_r, 3)), file=sys.stdout)
    print(lang["scintillation_attenuation"].format(np.round(a_s, 3)), file=sys.stdout)
    print(lang["total_atmospheric_attenuation"].format(np.round(a_t, 3)), file=sys.stdout)
    print(lang["free_space_attenuation"].format(np.round(a_fs, 3)), file=sys.stdout)
    print(lang["total_attenuation"].format(np.round(a_tot, 3)), file=sys.stdout)

    print(lang["reception_threshold"].format(np.round(satelite.get_reception_threshold(), 3)), file=sys.stdout)

    print('', file=sys.stdout)
    print(lang["runtime"].format(np.round(time.time() - start, 2)), file=sys.stdout)

    sys.stdout.close()

    path = convert_path_os('temp\\args.pkl')
    if os.path.exists(path):
        os.remove(path)
    return

def mp_link_performance():
    path = convert_path_os('temp\\args.pkl')
    with open(path, 'rb') as f:
        (gr_station_path, sat_long, freq, max_eirp, sat_height, max_bw, bw_util, modcod, pol,
         roll_off, ant_size, ant_eff, lnb_gain, lnb_temp, coupling_loss, cable_loss, max_depoint,
         snr_relaxation, margin, threads) = pickle.load(f)
        f.close()

    point_list = pd.read_csv(gr_station_path, sep=';', encoding='latin1')
    point_list['availability'] = np.nan

    path = convert_path_os('models\\Modulation_dB.csv')
    data = pd.read_csv(path, sep=';')
    line = data.loc[(data.Modcod) == modcod]
    mod = line['Modulation'].values[0]
    fec = line['FEC'].values[0]

    sat = Satellite(sat_long, freq, max_eirp, sat_height, max_bw, bw_util, 0, 0, mod, roll_off, fec)

    polarization_loss = 3
    reception = Reception(ant_size, ant_eff, coupling_loss, polarization_loss, lnb_gain, lnb_temp, cable_loss, max_depoint)

    pool = ParallelPool(nodes=threads)

    path = convert_path_os('temp\\out.txt')
    sys.stderr = open(path, 'w')

    print('initializing . . .', file=sys.stderr)

    data = list(
        tqdm.tqdm(pool.imap(point_availability,
                            [(point, sat, reception, margin, snr_relaxation) for index, point in point_list.iterrows()]),
                  total=len(point_list)))
    pool.clear()

    point_list.drop(point_list.index, inplace=True)
    point_list = point_list.append(data, ignore_index=True)
    point_list['unavailability time (min)'] = round(((100 - point_list['availability']) / 100) * 525600, 0)

    dir = 'results'
    if not os.path.exists(dir):
        os.makedirs(dir)

    path = convert_path_os(dir + '\\' + 'results ' + datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S') + '.csv')
    point_list.to_csv(path, sep=';', encoding='latin1')

    print('Complete!!!', file=sys.stderr)

    sys.stderr.close()

    return