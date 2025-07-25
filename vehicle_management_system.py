import pandas as pd
import streamlit as st
import io
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="车辆管理系统",
    page_icon="🚗",
    layout="wide"
)

# 页面标题
st.title("车辆管理系统")

# 读取模板数据
@st.cache_data
def load_template_data():
    try:
        df = pd.read_excel("template.xlsx")
        return df
    except Exception as e:
        st.error(f"读取模板文件失败: {e}")
        return None

# 初始化会话状态
if 'data' not in st.session_state:
    st.session_state.data = load_template_data()

# 侧边栏导航
menu = st.sidebar.selectbox(
    "选择功能",
    ["车辆数据", "司机数据", "原始数据"]
)

# 车辆数据页面
if menu == "车辆数据":
    st.subheader("车辆数据统计")
    
    if st.session_state.data is not None:
        # 计算每辆车的总加油金额、总行驶里程、常用司机
        vehicle_data = {}
        driver_usage = {}
        
        for _, row in st.session_state.data.iterrows():
            license_plate = row['车牌']
            driver = row['填写人']
            if pd.notna(license_plate):  # 确保车牌不为空
                # 计算行驶里程
                if pd.notna(row['还车时公里数']) and pd.notna(row['初始公里数']):
                    mileage = row['还车时公里数'] - row['初始公里数']
                else:
                    mileage = 0
                
                # 计算加油金额
                fuel_cost = row['加油金额'] if pd.notna(row['加油金额']) else 0
                
                if license_plate not in vehicle_data:
                    vehicle_data[license_plate] = {'总加油金额': 0, '总行驶里程': 0}
                    driver_usage[license_plate] = {}
                
                vehicle_data[license_plate]['总加油金额'] += fuel_cost
                vehicle_data[license_plate]['总行驶里程'] += mileage
                
                # 记录司机使用情况
                if pd.notna(driver):
                    if driver not in driver_usage[license_plate]:
                        driver_usage[license_plate][driver] = 0
                    driver_usage[license_plate][driver] += 1
        
        # 转换为DataFrame
        vehicle_df = pd.DataFrame.from_dict(vehicle_data, orient='index').reset_index()
        vehicle_df.columns = ['车牌号', '总加油金额', '总行驶里程']
        
        # 计算每公里油耗
        vehicle_df['每公里油耗（元）'] = vehicle_df['总加油金额'] / vehicle_df['总行驶里程'].where(vehicle_df['总行驶里程'] != 0, 1)
        
        # 确定常用司机
        vehicle_df['常用司机'] = ''
        for i, row in vehicle_df.iterrows():
            license_plate = row['车牌号']
            if license_plate in driver_usage and driver_usage[license_plate]:
                max_usage = max(driver_usage[license_plate].values())
                common_drivers = [driver for driver, count in driver_usage[license_plate].items() if count == max_usage]
                vehicle_df.at[i, '常用司机'] = '/'.join(common_drivers)
        
        # 显示表格
        st.dataframe(vehicle_df)
        
        # 下载按钮
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='车辆数据')
            return output.getvalue()
        
        excel_data = convert_df_to_excel(vehicle_df)
        st.download_button(
            label="下载车辆数据",
            data=excel_data,
            file_name="车辆数据.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("请先导入数据")

# 司机数据页面
elif menu == "司机数据":
    st.subheader("司机数据统计")
    
    if st.session_state.data is not None:
        # 计算每个司机的总加油金额、总行驶里程、出车次数、出车天数、常用车辆
        driver_data = {}
        vehicle_usage = {}
        trip_count = {}
        trip_days = {}
        
        for _, row in st.session_state.data.iterrows():
            driver = row['填写人']
            license_plate = row['车牌']
            if pd.notna(driver):  # 确保司机不为空
                # 计算行驶里程
                if pd.notna(row['还车时公里数']) and pd.notna(row['初始公里数']):
                    mileage = row['还车时公里数'] - row['初始公里数']
                else:
                    mileage = 0
                
                # 计算加油金额
                fuel_cost = row['加油金额'] if pd.notna(row['加油金额']) else 0
                
                # 计算出车天数
                days = row['预计用车天数'] if pd.notna(row['预计用车天数']) else 0
                
                if driver not in driver_data:
                    driver_data[driver] = {'总加油金额': 0, '总行驶里程': 0}
                    vehicle_usage[driver] = {}
                    trip_count[driver] = 0
                    trip_days[driver] = 0
                
                driver_data[driver]['总加油金额'] += fuel_cost
                driver_data[driver]['总行驶里程'] += mileage
                trip_count[driver] += 1
                trip_days[driver] += days
                
                # 记录车辆使用情况
                if pd.notna(license_plate):
                    if license_plate not in vehicle_usage[driver]:
                        vehicle_usage[driver][license_plate] = 0
                    vehicle_usage[driver][license_plate] += 1
        
        # 转换为DataFrame
        driver_df = pd.DataFrame.from_dict(driver_data, orient='index').reset_index()
        driver_df.columns = ['司机名', '总加油金额', '总行驶里程']
        
        # 添加出车次数和出车天数
        driver_df['出车次数'] = driver_df['司机名'].map(trip_count)
        driver_df['出车天数'] = driver_df['司机名'].map(trip_days)
        
        # 计算每公里油耗
        driver_df['每公里油耗（元）'] = driver_df['总加油金额'] / driver_df['总行驶里程'].where(driver_df['总行驶里程'] != 0, 1)
        
        # 确定常用车辆
        driver_df['常用车辆'] = ''
        for i, row in driver_df.iterrows():
            driver = row['司机名']
            if driver in vehicle_usage and vehicle_usage[driver]:
                max_usage = max(vehicle_usage[driver].values())
                common_vehicles = [vehicle for vehicle, count in vehicle_usage[driver].items() if count == max_usage]
                driver_df.at[i, '常用车辆'] = '/'.join(common_vehicles)
        
        # 显示表格
        st.dataframe(driver_df)
        
        # 下载按钮
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='司机数据')
            return output.getvalue()
        
        excel_data = convert_df_to_excel(driver_df)
        st.download_button(
            label="下载司机数据",
            data=excel_data,
            file_name="司机数据.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("请先导入数据")

# 原始数据页面
elif menu == "原始数据":
    st.subheader("原始数据管理")
    
    # 导出模板
    def export_template():
        try:
            with open("template.xlsx", "rb") as f:
                return f.read()
        except Exception as e:
            st.error(f"读取模板文件失败: {e}")
            return None
    
    template_data = export_template()
    if template_data is not None:
        st.download_button(
            label="导出模板",
            data=template_data,
            file_name="template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # 导入数据
    uploaded_file = st.file_uploader("导入数据", type=["xlsx"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.data = df
            st.success("数据导入成功！")
            st.dataframe(df)
        except Exception as e:
            st.error(f"导入数据失败: {e}")
    
    # 显示当前数据
    if st.session_state.data is not None:
        st.subheader("当前数据")
        st.dataframe(st.session_state.data)
    else:
        st.info("暂无数据，请导入数据")