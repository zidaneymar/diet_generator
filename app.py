import streamlit as st
import json
from main import medicinal_foods, seasonal_ingredients
from enhanced_diet_generator import EnhancedDietGenerator

# 设置页面标题
st.set_page_config(page_title="中医食疗推荐系统", layout="wide")

st.title("中医食疗推荐系统")
st.write("根据您的体质特征，生成个性化的一周膳食计划")

# 创建侧边栏用于用户输入
with st.sidebar:
    st.subheader("个人信息")
    
    # 体质类型选择
    main_type = st.selectbox(
        "主要体质类型",
        options=list(medicinal_foods.keys()),
        index=0
    )
    
    sub_type = st.selectbox(
        "次要体质类型",
        options=list(medicinal_foods.keys()),
        index=1 if len(medicinal_foods.keys()) > 1 else 0
    )
    
    # 性别选择
    gender = st.radio("性别", ["男", "女"])
    
    # 其他参数
    age = st.slider("年龄", 18, 80, 35)
    height = st.slider("身高(cm)", 140, 200, 165)
    weight = st.slider("体重(kg)", 40, 150, 70)
    
    # 活动量选择
    activity = st.selectbox(
        "日常活动量",
        options=["轻体力", "中等体力", "重体力"],
        index=1
    )
    
    # 疾病信息
    diseases = st.multiselect(
        "基础疾病(可多选)",
        options=["高血压", "糖尿病", "高血脂", "痛风", "无"],
        default=["无"]
    )
    
    # 饮食偏好
    preferred_cuisine = st.selectbox(
        "饮食偏好",
        options=["粤菜", "川菜", "湘菜", "鲁菜", "苏菜", "浙菜", "闽菜", "徽菜"],
        index=0
    )
    
    # 季节选择
    season = st.selectbox(
        "当前季节",
        options=list(seasonal_ingredients.keys()),
        index=0
    )
    
    # 选择生成器
    generator_type = st.radio(
        "选择生成器",
        ["基础版", "增强版(包含菜系、多样性和营养均衡)"],
        index=1
    )
    
    # 生成按钮
    generate_button = st.button("生成食疗推荐")

# 主内容区域
if generate_button:
    # 收集用户数据
    user_data = {
        "main_type": main_type,
        "sub_type": sub_type,
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "activity": activity,
        "diseases": diseases,
        "preferred_cuisine": preferred_cuisine,
        "season": season
    }
    
    try:
        # 根据用户选择的生成器类型实例化生成器
        if generator_type == "基础版":
            from main import DietGenerator
            generator = DietGenerator(user_data)
        else:
            generator = EnhancedDietGenerator(user_data)
            
        weekly_menu = generator.generate_weekly_menu()
        
        # 计算BMI和每日所需热量
        st.subheader("身体指标")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("BMI指数", f"{generator.bmi:.1f}")
            if generator.bmi < 18.5:
                st.info("体重偏低")
            elif generator.bmi < 24:
                st.success("体重正常")
            elif generator.bmi < 28:
                st.warning("超重")
            else:
                st.error("肥胖")
        
        with col2:
            st.metric("每日基础热量需求", f"{generator.calorie_needs:.0f} 千卡")
        
        # 显示推荐的药食同源食材
        st.subheader("推荐的药食同源食材")
        medicinals = generator._select_medicinal()
        st.write(", ".join(medicinals))
        
        # 添加饮食提示信息（仅增强版显示）
        if generator_type != "基础版":
            st.subheader("饮食提示")
            # 显示根据用户情况的饮食建议
            if "糖尿病" in diseases:
                st.info("⚠️ 糖尿病提示：已为您减少碳水化合物和高糖食物，增加低GI食物。")
            elif "高血压" in diseases:
                st.info("⚠️ 高血压提示：已为您减少钠盐含量高的食物，增加钾含量丰富的蔬果。")
            elif "高血脂" in diseases:
                st.info("⚠️ 高血脂提示：已为您减少动物性脂肪，增加不饱和脂肪酸食物。")
            elif "痛风" in diseases:
                st.info("⚠️ 痛风提示：已为您减少高嘌呤食物，建议保持充分饮水。")
        
        # 显示一周菜单
        st.subheader("一周膳食计划")
        
        # 使用选项卡显示每天的菜单
        tabs = st.tabs([f"第{i+1}天" for i in range(7)])
        
        for i, (day, tab) in enumerate(zip(weekly_menu.keys(), tabs)):
            with tab:
                for meal_type, meal in weekly_menu[day].items():
                    st.write(f"#### {meal_type}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**主食**: {meal['主食']}")
                        st.write(f"**热量**: {meal['热量']}")
                    
                    with col2:
                        st.write("**菜品**:")
                        for dish in meal['菜品']:
                            st.write(f"- {dish}")
                        st.write(f"**营养素比例**: {meal['营养素']}")
                    
                    st.divider()
    except Exception as e:
        st.error(f"生成食谱时出错: {str(e)}")
        st.info("如果您选择了增强版生成器，请确保已运行 process_food_data.py 脚本。")
else:
    st.info("请在左侧填写您的个人信息，然后点击「生成食疗推荐」按钮获取个性化的膳食计划。")
    
    # 显示一些介绍信息
    st.subheader("中医食疗的基本原则")
    st.write("""
    中医食疗是在中医理论指导下，根据食物的性味和归经特点，结合个人体质特点，通过合理调配食物，达到防病治病、保健养生的一种方法。
    
    主要原则包括：
    1. **辨证施膳**：根据体质和证型选择适合的食物
    2. **食药同源**：运用药食同源的食材增强食疗效果
    3. **因时制宜**：根据季节选择合适的食材
    4. **因人而异**：考虑个人体质、年龄、性别等特点
    """)
    
    # 显示关于各种体质的信息
    st.subheader("常见体质类型")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**胃热火郁**")
        st.write("表现：口干口苦、容易饥饿、大便干结")
        st.write("宜食：清热食物如苦瓜、荷叶、绿豆")
        
        st.write("**脾虚不运**")
        st.write("表现：食欲不振、腹胀、大便稀溏")
        st.write("宜食：健脾食物如山药、白扁豆、大枣")
        
        st.write("**脾肾阳虚**")
        st.write("表现：四肢发冷、腰膝酸软、畏寒怕冷")
        st.write("宜食：温补食物如肉桂、干姜、羊肉")
    
    with col2:
        st.write("**痰湿内盛**")
        st.write("表现：体重超标、身重困倦、易疲乏")
        st.write("宜食：祛湿食物如冬瓜、薏苡仁、茯苓")
        
        st.write("**气郁血瘀**")
        st.write("表现：胸胁胀满、情绪不稳、经期不调")
        st.write("宜食：理气活血食物如玫瑰花、桃仁、当归") 