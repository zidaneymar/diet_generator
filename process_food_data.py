import json
import random
import os

def load_food_data():
    """加载食物数据库并进行预处理"""
    try:
        with open('food_data/food-table.json', 'r', encoding='utf-8') as f:
            content = f.read()
            # 尝试修复JSON格式问题
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # 如果是多行JSON对象，尝试逐行解析
                lines = content.strip().split('\n')
                data = []
                for line in lines:
                    if line.strip():
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except:
                            print(f"无法解析行: {line[:50]}...")
        
        print(f"成功加载食物数据，共有{len(data)}条记录")
        return data
    except Exception as e:
        print(f"加载食物数据时出错: {str(e)}")
        return []

def categorize_foods(foods):
    """对食物进行分类"""
    categories = {}
    
    for food in foods:
        food_type = food.get('type', '其他')
        if food_type not in categories:
            categories[food_type] = []
        categories[food_type].append(food)
    
    return categories

def analyze_nutrition_data(foods):
    """分析食物的营养数据"""
    nutrition_stats = {
        "能量": [],
        "蛋白质": [],
        "脂肪": [],
        "碳水化合物": []
    }
    
    for food in foods:
        info = food.get('info', {})
        
        # 提取营养素数值
        for nutrient in nutrition_stats.keys():
            if nutrient in info:
                value_str = info[nutrient]
                # 提取数字
                try:
                    # 去掉单位和其他字符，只保留数值
                    numeric_value = ''.join(c for c in value_str if c.isdigit() or c == '.')
                    if numeric_value:
                        value = float(numeric_value)
                        nutrition_stats[nutrient].append((food['name'], value))
                except:
                    pass
    
    # 对每种营养素进行排序
    for nutrient in nutrition_stats:
        nutrition_stats[nutrient].sort(key=lambda x: x[1], reverse=True)
    
    return nutrition_stats

def create_cuisine_cooking_methods():
    """创建各种菜系的特色烹饪方法"""
    cuisine_methods = {
        "粤菜": ["清蒸", "白灼", "煲汤", "炒", "焖"],
        "川菜": ["麻辣", "干煸", "回锅", "水煮", "爆炒"],
        "湘菜": ["香辣", "腊制", "烟熏", "干锅", "蒸炒"],
        "鲁菜": ["爆", "炸", "烧", "蒸", "煨"],
        "苏菜": ["红烧", "清炖", "煮", "焖", "炒"],
        "浙菜": ["炖", "炒", "蒸", "烤", "煎"],
        "闽菜": ["红糟", "醉", "烧", "焖", "煮"],
        "徽菜": ["炖", "蒸", "烧", "炒", "熏"]
    }
    
    cuisine_flavors = {
        "粤菜": ["鲜", "清淡", "平和"],
        "川菜": ["麻辣", "辣", "香"], 
        "湘菜": ["香辣", "咸鲜"],
        "鲁菜": ["醇厚", "咸鲜"],
        "苏菜": ["甜", "清淡", "鲜"],
        "浙菜": ["鲜", "清淡"],
        "闽菜": ["清鲜", "酸甜"],
        "徽菜": ["醇厚", "浓郁"]
    }
    
    return cuisine_methods, cuisine_flavors

def enhance_diet_generator(food_data):
    """增强饮食生成器的功能"""
    # 1. 分类食物
    categorized_foods = categorize_foods(food_data)
    
    # 2. 分析营养数据
    nutrition_stats = analyze_nutrition_data(food_data)
    
    # 3. 获取烹饪方法
    cuisine_methods, cuisine_flavors = create_cuisine_cooking_methods()
    
    # 将食物按类型组织
    food_by_type = {}
    for food in food_data:
        food_type = food.get('type', '其他')
        if food_type not in food_by_type:
            food_by_type[food_type] = []
        food_by_type[food_type].append(food)
    
    # 组织各种食物类别的数据
    food_categories = {
        "主食": ["谷类", "薯类"],
        "蛋白质": ["豆类", "畜肉", "禽肉", "蛋类", "河海鲜"],
        "蔬菜": ["蔬菜", "菌类", "藻类"],
        "水果": ["水果"],
        "坚果": ["坚果"],
        "调味品": ["调味品类", "油类"],
        "饮品": ["茶类", "酒类", "零食饮料"]
    }
    
    # 构建逆向映射
    food_type_to_category = {}
    for category, types in food_categories.items():
        for type_name in types:
            food_type_to_category[type_name] = category
    
    return {
        "categorized_foods": categorized_foods,
        "nutrition_stats": nutrition_stats,
        "cuisine_methods": cuisine_methods,
        "cuisine_flavors": cuisine_flavors,
        "food_by_type": food_by_type,
        "food_categories": food_categories,
        "food_type_to_category": food_type_to_category
    }

def export_diet_generator_helper(food_data):
    """导出增强的饮食生成器辅助数据"""
    enhanced_data = enhance_diet_generator(food_data)
    
    # 创建输出目录
    os.makedirs('food_data/processed', exist_ok=True)
    
    # 保存增强数据
    with open('food_data/processed/diet_helper_data.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
    
    print("已将处理后的数据保存到 food_data/processed/diet_helper_data.json")
    
    # 返回结果以便后续使用
    return enhanced_data

if __name__ == "__main__":
    food_data = load_food_data()
    if food_data:
        export_diet_generator_helper(food_data) 