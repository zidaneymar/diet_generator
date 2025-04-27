import json
import pandas as pd
import random
from typing import Dict, List

# ---------- 数据层 ----------
# 加载中药食同源数据库 (示例)
medicinal_foods = {
    "胃热火郁": ["荷叶", "栀子", "决明子", "麦芽"],
    "痰湿内盛": ["茯苓", "薏苡仁", "陈皮", "山楂"],
    "气郁血瘀": ["当归", "桃仁", "佛手", "玫瑰花"],
    "脾虚不运": ["黄芪", "山药", "白扁豆", "砂仁"],
    "脾肾阳虚": ["肉桂", "干姜", "芡实", "肉苁蓉"]
}

# 加载时令食材数据库 (示例)
seasonal_ingredients = {
    "春季": ["菠菜", "荠菜", "春笋"],
    "夏季": ["苦瓜", "冬瓜", "绿豆"],
    "秋季": ["莲藕", "银耳", "百合"],
    "冬季": ["羊肉", "黑豆", "核桃"]
}

# ---------- 核心算法 ----------
class DietGenerator:
    def __init__(self, user_data: Dict):
        self.user_data = user_data
        self.bmi = user_data["weight"] / (user_data["height"]/100)**2
        self.calorie_needs = self._calculate_calorie()
        
    def _calculate_calorie(self) -> float:
        """根据Harris-Benedict公式计算基础代谢"""
        if self.user_data["gender"] == "男":
            bmr = 88.362 + 13.397*self.user_data["weight"] + 4.799*self.user_data["height"] - 5.677*self.user_data["age"]
        else:
            bmr = 447.593 + 9.247*self.user_data["weight"] + 3.098*self.user_data["height"] - 4.330*self.user_data["age"]
        
        # 根据活动量调整
        activity_level = {"轻体力":1.2, "中等体力":1.55, "重体力":1.9}
        return round(bmr * activity_level[self.user_data["activity"]] * 0.85, 0)  # 制造热量缺口

    def _select_medicinal(self) -> List[str]:
        """选择药食同源药材"""
        main_type = self.user_data["main_type"]
        return medicinal_foods.get(main_type, []) + medicinal_foods.get(self.user_data["sub_type"], [])

    def generate_weekly_menu(self) -> Dict:
        """生成一周菜谱"""
        menu = {}
        for day in range(1, 8):
            menu[f"Day{day}"] = {
                "早餐": self._generate_meal("早餐"),
                "午餐": self._generate_meal("午餐"),
                "晚餐": self._generate_meal("晚餐")
            }
        return menu

    def _generate_meal(self, meal_type: str) -> Dict:
        """生成单餐数据（需接入食材数据库）"""
        # 根据餐点类型调整主食和热量
        if meal_type == "早餐":
            main_food_options = ["全麦面包", "燕麦粥", "杂粮粥", "小米粥", "馒头"]
            calorie = f"{random.randint(350, 450)}kcal"
        elif meal_type == "午餐":
            main_food_options = ["杂粮饭", "糙米饭", "全麦面条", "米粉", "荞麦面"]
            calorie = f"{random.randint(500, 600)}kcal"
        else:  # 晚餐
            main_food_options = ["小米饭", "糙米饭", "薏米饭", "藜麦饭", "紫米饭"]
            calorie = f"{random.randint(400, 500)}kcal"
            
        # 随机选择主食
        main_food = random.choice(main_food_options)
        
        # 随机选择1-3种药材
        medicinals = self._select_medicinal()
        selected_medicinals = random.sample(medicinals, min(random.randint(1, 3), len(medicinals)))
        
        # 随机生成2-3道菜品
        dish_count = random.randint(2, 3)
        dishes = []
        
        for i in range(dish_count):
            if i == 0:
                # 第一道菜总是蔬菜
                vegetable = self._select_vegetable()
                cooking_methods = ["清炒", "凉拌", "爆炒", "蒸", "炖"]
                dishes.append(f"{random.choice(cooking_methods)}{vegetable}（{vegetable} {random.randint(150, 250)}g，调料适量）")
            elif i == 1:
                # 第二道菜总是蛋白质
                protein = self._select_protein()
                cooking_methods = ["煮", "蒸", "炖", "烤", "煎"]
                dishes.append(f"{random.choice(cooking_methods)}{protein}（{protein} {random.randint(80, 150)}g，药材：{', '.join(selected_medicinals[:1])} 适量）")
            else:
                # 可能的第三道菜
                seasonal = random.choice(seasonal_ingredients.get(self.user_data["season"], ["时令蔬菜"]))
                cooking_methods = ["炒", "炖", "煮", "凉拌"]
                dishes.append(f"{random.choice(cooking_methods)}{seasonal}（{seasonal} {random.randint(100, 200)}g）")
        
        # 随机调整营养素比例
        carbs = random.randint(40, 55)
        protein = random.randint(20, 30)
        fat = 100 - carbs - protein
        
        return {
            "主食": main_food,
            "菜品": dishes,
            "热量": calorie,
            "营养素": f"碳水{carbs}% 蛋白{protein}% 脂肪{fat}%"
        }

    # ---------- 辅助方法 ----------
    def _select_vegetable(self):
        """根据证型选择蔬菜"""
        type_map = {
            "胃热火郁": ["苦瓜", "黄瓜", "西葫芦", "菠菜", "莴笋"],
            "痰湿内盛": ["冬瓜", "白萝卜", "青萝卜", "黄花菜", "丝瓜"],
            "气郁血瘀": ["茄子", "西红柿", "胡萝卜", "油菜", "芹菜"],
            "脾虚不运": ["南瓜", "山药", "红薯", "土豆", "莲藕"],
            "脾肾阳虚": ["韭菜", "生姜", "洋葱", "香菜", "大葱"]
        }
        
        # 结合季节性蔬菜
        seasonal_vegs = seasonal_ingredients.get(self.user_data["season"], [])
        
        # 获取体质对应的蔬菜列表，如果没有则使用默认蔬菜
        veg_list = type_map.get(self.user_data["main_type"], ["菠菜", "西红柿", "青菜"])
        
        # 结合体质蔬菜和季节蔬菜
        combined_list = veg_list + [veg for veg in seasonal_vegs if veg not in veg_list]
        
        # 随机选择一种蔬菜
        return random.choice(combined_list)

    def _select_protein(self):
        """根据基础疾病选择蛋白质"""
        # 基本蛋白质食物库
        proteins = {
            "植物蛋白": ["豆腐", "豆干", "豆皮", "黑豆", "黄豆"],
            "海鲜": ["虾", "鱼", "蟹", "带鱼", "鲈鱼"],
            "家禽": ["鸡胸肉", "鸭肉", "鹅肉", "鸡蛋"],
            "红肉": ["瘦猪肉", "牛肉", "羊肉"]
        }
        
        # 疾病限制
        if "糖尿病" in self.user_data["diseases"]:
            # 优先选择低糖分的蛋白质
            combined = proteins["植物蛋白"] + proteins["家禽"]
        elif "高血压" in self.user_data["diseases"]:
            # 避免高盐食品
            combined = proteins["植物蛋白"] + proteins["家禽"] + proteins["海鲜"][:2]
        elif "高血脂" in self.user_data["diseases"]:
            # 避免高脂肪食品
            combined = proteins["植物蛋白"] + ["鸡胸肉", "鱼"]
        elif "痛风" in self.user_data["diseases"]:
            # 避免高嘌呤食品
            combined = proteins["植物蛋白"] + ["鸡胸肉", "鸡蛋"]
        else:
            # 无疾病限制，从所有类别中随机选择
            combined = []
            for category in proteins.values():
                combined.extend(category)
        
        # 随机选择一种蛋白质
        return random.choice(combined)

# ---------- 使用示例 ----------
if __name__ == "__main__":
    sample_data = {
        "main_type": "痰湿内盛",
        "sub_type": "脾虚不运",
        "gender": "女",
        "age": 35,
        "height": 165,
        "weight": 70,
        "activity": "中等体力",
        "diseases": ["高血压"],
        "preferred_cuisine": "粤菜",
        "season": "夏季"
    }
    
    generator = DietGenerator(sample_data)
    print(json.dumps(generator.generate_weekly_menu(), indent=2, ensure_ascii=False))