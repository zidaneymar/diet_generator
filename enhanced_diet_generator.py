import json
import random
from typing import Dict, List

# 加载处理好的食物数据
def load_diet_helper_data():
    try:
        with open('food_data/processed/diet_helper_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载食物数据时出错: {str(e)}")
        return None

class EnhancedDietGenerator:
    def __init__(self, user_data: Dict):
        self.user_data = user_data
        self.bmi = user_data["weight"] / (user_data["height"]/100)**2
        self.calorie_needs = self._calculate_calorie()
        
        # 加载食物数据库
        self.diet_helper_data = load_diet_helper_data()
        if not self.diet_helper_data:
            raise ValueError("无法加载食物数据库，请确保已经运行 process_food_data.py")
        
        # 确保用一周内不会重复相同的主食和蛋白质
        self.used_staples = set()  # 已使用的主食
        self.used_proteins = set()  # 已使用的蛋白质来源
        
        # 初始化7天的记录
        self.weekly_record = {f"Day{i+1}": {"主食": [], "蛋白质": [], "蔬菜": [], "水果": []} for i in range(7)}
        
    def _calculate_calorie(self) -> float:
        """根据Harris-Benedict公式计算基础代谢"""
        if self.user_data["gender"] == "男":
            bmr = 88.362 + 13.397*self.user_data["weight"] + 4.799*self.user_data["height"] - 5.677*self.user_data["age"]
        else:
            bmr = 447.593 + 9.247*self.user_data["weight"] + 3.098*self.user_data["height"] - 4.330*self.user_data["age"]
        
        # 根据活动量调整
        activity_level = {"轻体力":1.2, "中等体力":1.55, "重体力":1.9}
        
        # 根据BMI调整热量
        bmi_adjustment = 1.0
        if self.bmi > 28:  # 肥胖
            bmi_adjustment = 0.8
        elif self.bmi > 24:  # 超重
            bmi_adjustment = 0.85
        elif self.bmi < 18.5:  # 偏瘦
            bmi_adjustment = 1.1
        
        return round(bmr * activity_level[self.user_data["activity"]] * bmi_adjustment, 0)

    def _select_medicinal(self) -> List[str]:
        """选择药食同源药材"""
        from test import medicinal_foods
        main_type = self.user_data["main_type"]
        return medicinal_foods.get(main_type, []) + medicinal_foods.get(self.user_data["sub_type"], [])

    def _select_ingredients_by_cuisine(self, food_type):
        """根据用户偏好的菜系选择食材和烹饪方法"""
        preferred_cuisine = self.user_data["preferred_cuisine"]
        cuisine_methods = self.diet_helper_data['cuisine_methods'].get(preferred_cuisine, [])
        cuisine_flavors = self.diet_helper_data['cuisine_flavors'].get(preferred_cuisine, [])
        
        # 如果没有特定菜系方法，使用通用方法
        if not cuisine_methods:
            cuisine_methods = ["炒", "煮", "蒸", "烤", "煎"]
            
        if not cuisine_flavors:
            cuisine_flavors = ["鲜", "香", "咸", "甜"]
        
        # 随机选择烹饪方法和口味
        cooking_method = random.choice(cuisine_methods)
        flavor = random.choice(cuisine_flavors)
        
        return cooking_method, flavor

    def _get_seasonal_fruits(self):
        """获取当季水果"""
        season = self.user_data["season"]
        seasonal_fruits = []
        
        # 从食物数据库中筛选出水果类
        all_fruits = self.diet_helper_data['food_by_type'].get('水果', [])
        
        # 简化的季节水果对应关系
        season_mapping = {
            "春季": ["草莓", "樱桃", "枇杷", "杨梅"],
            "夏季": ["西瓜", "桃子", "荔枝", "葡萄", "杏"],
            "秋季": ["苹果", "梨", "柿子", "猕猴桃", "柚子"],
            "冬季": ["橙子", "橘子", "柚子", "香蕉", "火龙果"]
        }
        
        # 获取当季水果
        seasonal_names = season_mapping.get(season, [])
        
        # 筛选存在于数据库中的当季水果
        for fruit in all_fruits:
            fruit_name = fruit.get('name', '')
            for seasonal_name in seasonal_names:
                if seasonal_name in fruit_name:
                    seasonal_fruits.append(fruit)
        
        # 如果当季水果不足，添加一些通用水果
        common_fruits = ["苹果", "香蕉", "橙子"]
        if len(seasonal_fruits) < 3:
            for fruit in all_fruits:
                fruit_name = fruit.get('name', '')
                for common_name in common_fruits:
                    if common_name in fruit_name and fruit not in seasonal_fruits:
                        seasonal_fruits.append(fruit)
                        if len(seasonal_fruits) >= 5:
                            break
                if len(seasonal_fruits) >= 5:
                    break
        
        return seasonal_fruits or all_fruits[:5]  # 确保至少有一些水果可选
    
    def _avoid_repetition(self, food_list, used_items, day, meal_type, max_attempts=10):
        """尝试避免一周内重复食材"""
        attempts = 0
        while attempts < max_attempts:
            item = random.choice(food_list)
            item_name = item.get('name', '')
            
            # 检查是否已经在本周使用过
            if item_name not in used_items:
                # 记录这个选择
                used_items.add(item_name)
                self.weekly_record[day][meal_type].append(item_name)
                return item
                
            attempts += 1
        
        # 如果尝试多次仍无法避免重复，则接受重复
        item = random.choice(food_list)
        item_name = item.get('name', '')
        self.weekly_record[day][meal_type].append(item_name)
        return item

    def generate_weekly_menu(self) -> Dict:
        """生成一周菜谱"""
        menu = {}
        for day in range(1, 8):
            day_key = f"Day{day}"
            menu[day_key] = {
                "早餐": self._generate_meal("早餐", day_key),
                "午餐": self._generate_meal("午餐", day_key),
                "晚餐": self._generate_meal("晚餐", day_key)
            }
        return menu

    def _generate_meal(self, meal_type: str, day: str) -> Dict:
        """生成单餐数据（结合食物数据库）"""
        # 根据餐点类型调整主食和热量
        if meal_type == "早餐":
            main_food_options = self._get_breakfast_staples()
            calorie = f"{random.randint(350, 450)}kcal"
            fruit_included = True  # 早餐包含水果
        elif meal_type == "午餐":
            main_food_options = self._get_lunch_staples()
            calorie = f"{random.randint(500, 600)}kcal"
            fruit_included = False  # 午餐不一定包含水果
        else:  # 晚餐
            main_food_options = self._get_dinner_staples()
            calorie = f"{random.randint(400, 500)}kcal"
            fruit_included = random.choice([True, False])  # 晚餐有50%概率包含水果
        
        # 随机选择主食，避免重复
        main_food = self._avoid_repetition(main_food_options, self.used_staples, day, "主食")
        main_food_name = main_food.get('name', '未知主食')
        
        # 随机选择1-3种药材
        medicinals = self._select_medicinal()
        selected_medicinals = random.sample(medicinals, min(random.randint(1, 3), len(medicinals)))
        
        # 根据用户饮食偏好选择烹饪方法
        cooking_method, flavor = self._select_ingredients_by_cuisine(main_food.get('type', ''))
        
        # 随机生成2-4道菜品
        dish_count = random.randint(2, 4)
        dishes = []
        
        # 第一道菜总是蔬菜
        vegetable = self._select_vegetable_by_condition()
        veg_cooking_methods = ["清炒", "凉拌", "爆炒", "蒸", "炖"]
        veg_method = cooking_method if cooking_method in veg_cooking_methods else random.choice(veg_cooking_methods)
        dishes.append(f"{veg_method}{vegetable.get('name', '')}（{random.randint(150, 250)}g，{flavor}味）")
        
        # 第二道菜总是蛋白质
        protein = self._select_protein_by_condition()
        protein_cooking_methods = ["煮", "蒸", "炖", "烤", "煎"]
        protein_method = cooking_method if cooking_method in protein_cooking_methods else random.choice(protein_cooking_methods)
        dishes.append(f"{protein_method}{protein.get('name', '')}（{random.randint(80, 150)}g，药材：{', '.join(selected_medicinals[:1])} 适量）")
        
        # 可能的第三道菜 - 当季蔬菜或其他菜品
        if dish_count >= 3:
            seasonal_veg = self._select_seasonal_vegetable()
            seasonal_cooking_methods = ["炒", "炖", "煮", "凉拌"]
            seasonal_method = random.choice(seasonal_cooking_methods)
            dishes.append(f"{seasonal_method}{seasonal_veg.get('name', '')}（{random.randint(100, 200)}g）")
        
        # 可能的第四道菜 - 汤或甜点
        if dish_count >= 4:
            if random.choice([True, False]):  # 50%概率是汤
                soup_base = random.choice(["清汤", "番茄汤", "紫菜汤", "鸡汤", "排骨汤", "蘑菇汤"])
                dishes.append(f"{soup_base}（250ml）")
            else:  # 50%概率是甜点
                dessert = random.choice(["水果沙拉", "酸奶", "坚果", "红豆糕", "水果拼盘"])
                dishes.append(f"{dessert}（100g）")
        
        # 如果包含水果，添加水果
        if fruit_included:
            fruit = self._select_fruit()
            dishes.append(f"水果：{fruit.get('name', '')}（{random.randint(80, 150)}g）")
        
        # 随机调整营养素比例
        carbs = random.randint(40, 55)
        protein = random.randint(20, 30)
        fat = 100 - carbs - protein
        
        return {
            "主食": main_food_name,
            "菜品": dishes,
            "热量": calorie,
            "营养素": f"碳水{carbs}% 蛋白{protein}% 脂肪{fat}%"
        }

    def _get_breakfast_staples(self):
        """获取早餐主食选项"""
        breakfast_options = []
        
        # 从数据库筛选合适的早餐主食
        staple_types = ['谷类', '薯类']
        
        for food_type in staple_types:
            foods = self.diet_helper_data['food_by_type'].get(food_type, [])
            # 筛选适合早餐的食物
            for food in foods:
                name = food.get('name', '').lower()
                if any(item in name for item in ["粥", "面包", "馒头", "包子", "花卷", "饼", "三明治", "燕麦"]):
                    breakfast_options.append(food)
        
        # 如果没有找到足够的选项，添加一些固定选项
        if len(breakfast_options) < 5:
            default_options = [
                {"name": "全麦面包", "type": "谷类"},
                {"name": "燕麦粥", "type": "谷类"},
                {"name": "杂粮粥", "type": "谷类"},
                {"name": "小米粥", "type": "谷类"},
                {"name": "馒头", "type": "谷类"}
            ]
            for option in default_options:
                if option not in breakfast_options:
                    breakfast_options.append(option)
        
        return breakfast_options

    def _get_lunch_staples(self):
        """获取午餐主食选项"""
        lunch_options = []
        
        # 从数据库筛选合适的午餐主食
        staple_types = ['谷类', '薯类']
        
        for food_type in staple_types:
            foods = self.diet_helper_data['food_by_type'].get(food_type, [])
            # 筛选适合午餐的食物
            for food in foods:
                name = food.get('name', '').lower()
                if any(item in name for item in ["米饭", "面条", "米粉", "意面", "通心粉", "面", "饭"]):
                    lunch_options.append(food)
        
        # 如果没有找到足够的选项，添加一些固定选项
        if len(lunch_options) < 5:
            default_options = [
                {"name": "杂粮饭", "type": "谷类"},
                {"name": "糙米饭", "type": "谷类"},
                {"name": "全麦面条", "type": "谷类"},
                {"name": "米粉", "type": "谷类"},
                {"name": "荞麦面", "type": "谷类"}
            ]
            for option in default_options:
                if option not in lunch_options:
                    lunch_options.append(option)
        
        return lunch_options

    def _get_dinner_staples(self):
        """获取晚餐主食选项"""
        dinner_options = []
        
        # 从数据库筛选合适的晚餐主食
        staple_types = ['谷类', '薯类']
        
        for food_type in staple_types:
            foods = self.diet_helper_data['food_by_type'].get(food_type, [])
            # 筛选适合晚餐的食物
            for food in foods:
                name = food.get('name', '').lower()
                if any(item in name for item in ["米饭", "粥", "饭", "薯", "地瓜", "红薯"]):
                    dinner_options.append(food)
        
        # 如果没有找到足够的选项，添加一些固定选项
        if len(dinner_options) < 5:
            default_options = [
                {"name": "小米饭", "type": "谷类"},
                {"name": "糙米饭", "type": "谷类"},
                {"name": "薏米饭", "type": "谷类"},
                {"name": "藜麦饭", "type": "谷类"},
                {"name": "紫米饭", "type": "谷类"}
            ]
            for option in default_options:
                if option not in dinner_options:
                    dinner_options.append(option)
        
        return dinner_options

    def _select_vegetable_by_condition(self):
        """根据用户体质和疾病选择适合的蔬菜"""
        # 获取用户的体质类型
        body_type = self.user_data["main_type"]
        
        # 根据体质类型推荐蔬菜
        type_map = {
            "胃热火郁": ["苦瓜", "黄瓜", "西葫芦", "菠菜", "莴笋"],
            "痰湿内盛": ["冬瓜", "白萝卜", "青萝卜", "黄花菜", "丝瓜"],
            "气郁血瘀": ["茄子", "西红柿", "胡萝卜", "油菜", "芹菜"],
            "脾虚不运": ["南瓜", "山药", "红薯", "土豆", "莲藕"],
            "脾肾阳虚": ["韭菜", "生姜", "洋葱", "香菜", "大葱"]
        }
        
        # 从数据库中获取蔬菜类别的食物
        veggies = self.diet_helper_data['food_by_type'].get('蔬菜', [])
        
        # 根据体质推荐的蔬菜名称
        recommended_names = type_map.get(body_type, ["菠菜", "西红柿", "青菜"])
        
        # 匹配推荐蔬菜名称与数据库中的蔬菜
        recommended_veggies = []
        
        for veggie in veggies:
            veggie_name = veggie.get('name', '')
            for rec_name in recommended_names:
                if rec_name in veggie_name:
                    recommended_veggies.append(veggie)
                    break
        
        # 如果找不到匹配的蔬菜，使用所有蔬菜
        if not recommended_veggies:
            recommended_veggies = veggies
        
        # 随机选择一种蔬菜
        return random.choice(recommended_veggies) if recommended_veggies else {"name": "时令蔬菜", "type": "蔬菜"}

    def _select_seasonal_vegetable(self):
        """选择当季蔬菜"""
        season = self.user_data["season"]
        
        # 从食物数据库中筛选出蔬菜类
        all_veggies = self.diet_helper_data['food_by_type'].get('蔬菜', [])
        
        # 简化的季节蔬菜对应关系
        season_mapping = {
            "春季": ["春笋", "荠菜", "韭菜", "菠菜", "豌豆"],
            "夏季": ["冬瓜", "丝瓜", "茄子", "黄瓜", "苦瓜"],
            "秋季": ["白萝卜", "胡萝卜", "山药", "莲藕", "南瓜"],
            "冬季": ["白菜", "芹菜", "菠菜", "大葱", "花椰菜"]
        }
        
        # 获取当季蔬菜
        seasonal_names = season_mapping.get(season, [])
        
        # 筛选存在于数据库中的当季蔬菜
        seasonal_veggies = []
        
        for veggie in all_veggies:
            veggie_name = veggie.get('name', '')
            for seasonal_name in seasonal_names:
                if seasonal_name in veggie_name:
                    seasonal_veggies.append(veggie)
        
        # 如果当季蔬菜不足，使用所有蔬菜
        if not seasonal_veggies:
            seasonal_veggies = all_veggies
        
        # 随机选择一种当季蔬菜
        return random.choice(seasonal_veggies) if seasonal_veggies else {"name": "时令蔬菜", "type": "蔬菜"}

    def _select_protein_by_condition(self):
        """根据用户的疾病情况选择适合的蛋白质来源"""
        diseases = self.user_data["diseases"]
        
        # 蛋白质类别包括豆类、畜肉、禽肉、蛋类、河海鲜
        protein_types = ["豆类", "畜肉", "禽肉", "蛋类", "河海鲜"]
        protein_foods = []
        
        for food_type in protein_types:
            protein_foods.extend(self.diet_helper_data['food_by_type'].get(food_type, []))
        
        # 疾病限制
        if "糖尿病" in diseases:
            # 优先选择低糖分的蛋白质
            suitable_foods = [food for food in protein_foods 
                             if food.get('type') in ["豆类", "禽肉", "蛋类"]]
        elif "高血压" in diseases:
            # 避免高盐食品
            suitable_foods = [food for food in protein_foods 
                             if food.get('type') not in ["河海鲜"]]
        elif "高血脂" in diseases:
            # 避免高脂肪食品
            suitable_foods = [food for food in protein_foods 
                             if food.get('type') not in ["畜肉"]]
        elif "痛风" in diseases:
            # 避免高嘌呤食品
            suitable_foods = [food for food in protein_foods 
                             if food.get('type') not in ["河海鲜", "畜肉"]]
        else:
            # 无疾病限制
            suitable_foods = protein_foods
        
        # 如果没有合适的选择，使用豆类和禽肉作为默认选择
        if not suitable_foods:
            for food_type in ["豆类", "禽肉"]:
                suitable_foods.extend(self.diet_helper_data['food_by_type'].get(food_type, []))
        
        # 还是没有选择，提供默认值
        if not suitable_foods:
            return {"name": "豆腐", "type": "豆类"}
        
        # 随机选择一种蛋白质食物
        return random.choice(suitable_foods)

    def _select_fruit(self):
        """选择水果"""
        # 获取当季水果
        seasonal_fruits = self._get_seasonal_fruits()
        
        # 随机选择一种水果
        if seasonal_fruits:
            return random.choice(seasonal_fruits)
        else:
            return {"name": "时令水果", "type": "水果"}

# 测试代码
if __name__ == "__main__":
    # 测试数据
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
    
    try:
        generator = EnhancedDietGenerator(sample_data)
        weekly_menu = generator.generate_weekly_menu()
        print(json.dumps(weekly_menu, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"生成食谱时出错: {str(e)}") 