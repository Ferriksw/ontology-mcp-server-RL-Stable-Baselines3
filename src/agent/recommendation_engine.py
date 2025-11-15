"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI

Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
个性化推荐引擎

推荐策略：
1. 基于内容的推荐：根据商品属性（类别、品牌、价格）相似度
2. 协同过滤：基于用户行为相似度（浏览、购买历史）
3. 混合推荐：结合内容和协同过滤
4. 热门推荐：基于商品热度和销量
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import math


@dataclass
class Product:
    """商品信息"""
    product_id: str
    name: str
    category: str
    brand: str
    price: float
    tags: List[str] = field(default_factory=list)
    sales_count: int = 0
    rating: float = 0.0


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    
    # 行为历史
    viewed_products: List[str] = field(default_factory=list)       # 浏览过的商品
    purchased_products: List[str] = field(default_factory=list)    # 购买过的商品
    searched_keywords: List[str] = field(default_factory=list)     # 搜索关键词
    
    # 偏好统计
    preferred_categories: Dict[str, int] = field(default_factory=dict)  # 类别偏好
    preferred_brands: Dict[str, int] = field(default_factory=dict)      # 品牌偏好
    price_range: Tuple[float, float] = (0.0, float('inf'))              # 价格范围
    
    # VIP 信息
    is_vip: bool = False
    vip_level: int = 0
    
    def update_from_view(self, product: Product):
        """从浏览记录更新画像"""
        if product.product_id not in self.viewed_products:
            self.viewed_products.append(product.product_id)
        
        # 更新类别偏好
        self.preferred_categories[product.category] = \
            self.preferred_categories.get(product.category, 0) + 1
        
        # 更新品牌偏好
        self.preferred_brands[product.brand] = \
            self.preferred_brands.get(product.brand, 0) + 1
    
    def update_from_purchase(self, product: Product):
        """从购买记录更新画像（权重更高）"""
        if product.product_id not in self.purchased_products:
            self.purchased_products.append(product.product_id)
        
        # 购买行为的权重是浏览的3倍
        self.preferred_categories[product.category] = \
            self.preferred_categories.get(product.category, 0) + 3
        
        self.preferred_brands[product.brand] = \
            self.preferred_brands.get(product.brand, 0) + 3
        
        # 更新价格范围
        if self.price_range == (0.0, float('inf')):
            self.price_range = (product.price * 0.5, product.price * 2.0)
        else:
            min_price = min(self.price_range[0], product.price * 0.5)
            max_price = max(self.price_range[1], product.price * 2.0)
            self.price_range = (min_price, max_price)
    
    def update_from_search(self, keywords: List[str]):
        """从搜索记录更新画像"""
        self.searched_keywords.extend(keywords)
    
    def get_top_categories(self, top_n: int = 3) -> List[str]:
        """获取最喜欢的商品类别"""
        sorted_categories = sorted(
            self.preferred_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [cat for cat, _ in sorted_categories[:top_n]]
    
    def get_top_brands(self, top_n: int = 3) -> List[str]:
        """获取最喜欢的品牌"""
        sorted_brands = sorted(
            self.preferred_brands.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [brand for brand, _ in sorted_brands[:top_n]]


@dataclass
class RecommendationResult:
    """推荐结果"""
    product_id: str
    product_name: str
    score: float
    reason: str  # 推荐理由
    strategy: str  # 推荐策略


class RecommendationEngine:
    """个性化推荐引擎"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
    
    def add_product(self, product: Product):
        """添加商品"""
        self.products[product.product_id] = product
    
    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """获取或创建用户画像"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        return self.user_profiles[user_id]
    
    def update_user_profile_from_action(
        self,
        user_id: str,
        action: str,  # "view", "purchase", "search"
        product_id: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ):
        """从用户行为更新画像"""
        profile = self.get_or_create_user_profile(user_id)
        
        if action == "view" and product_id and product_id in self.products:
            profile.update_from_view(self.products[product_id])
        
        elif action == "purchase" and product_id and product_id in self.products:
            profile.update_from_purchase(self.products[product_id])
        
        elif action == "search" and keywords:
            profile.update_from_search(keywords)
    
    def recommend(
        self,
        user_id: str,
        top_n: int = 5,
        strategy: str = "hybrid"  # "content", "collaborative", "hybrid", "popular"
    ) -> List[RecommendationResult]:
        """生成推荐"""
        profile = self.get_or_create_user_profile(user_id)
        
        if strategy == "content":
            return self._content_based_recommend(profile, top_n)
        elif strategy == "collaborative":
            return self._collaborative_recommend(profile, top_n)
        elif strategy == "popular":
            return self._popular_recommend(top_n)
        else:  # hybrid
            return self._hybrid_recommend(profile, top_n)
    
    def _content_based_recommend(
        self,
        profile: UserProfile,
        top_n: int
    ) -> List[RecommendationResult]:
        """基于内容的推荐"""
        recommendations = []
        
        # 排除已购买的商品
        excluded_ids = set(profile.purchased_products)
        
        for product_id, product in self.products.items():
            if product_id in excluded_ids:
                continue
            
            score = 0.0
            reasons = []
            
            # 1. 类别匹配（权重 0.4）
            if product.category in profile.preferred_categories:
                category_score = profile.preferred_categories[product.category]
                score += 0.4 * min(category_score / 10, 1.0)  # 归一化到 0-0.4
                reasons.append(f"您喜欢{product.category}类商品")
            
            # 2. 品牌匹配（权重 0.3）
            if product.brand in profile.preferred_brands:
                brand_score = profile.preferred_brands[product.brand]
                score += 0.3 * min(brand_score / 10, 1.0)
                reasons.append(f"您喜欢{product.brand}品牌")
            
            # 3. 价格匹配（权重 0.2）
            if profile.price_range[0] <= product.price <= profile.price_range[1]:
                score += 0.2
                reasons.append(f"价格在您的预算范围内")
            
            # 4. 标签匹配（权重 0.1）
            for keyword in profile.searched_keywords:
                if any(keyword.lower() in tag.lower() for tag in product.tags):
                    score += 0.1
                    reasons.append(f"与您搜索的'{keyword}'相关")
                    break
            
            if score > 0:
                recommendations.append(RecommendationResult(
                    product_id=product_id,
                    product_name=product.name,
                    score=score,
                    reason="; ".join(reasons),
                    strategy="content-based"
                ))
        
        # 按分数排序
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_n]
    
    def _collaborative_recommend(
        self,
        profile: UserProfile,
        top_n: int
    ) -> List[RecommendationResult]:
        """协同过滤推荐（简化版：基于"购买了A的用户也购买了B"）"""
        recommendations = []
        
        # 找到相似用户（购买了相同商品的用户）
        similar_users = []
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id == profile.user_id:
                continue
            
            # 计算相似度（Jaccard 相似度）
            purchased_set = set(profile.purchased_products)
            other_purchased_set = set(other_profile.purchased_products)
            
            if not purchased_set:
                continue
            
            intersection = purchased_set & other_purchased_set
            union = purchased_set | other_purchased_set
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > 0.1:  # 相似度阈值
                    similar_users.append((other_user_id, similarity, other_profile))
        
        # 统计相似用户购买的商品
        product_scores = defaultdict(float)
        excluded_ids = set(profile.purchased_products)
        
        for _, similarity, other_profile in similar_users:
            for product_id in other_profile.purchased_products:
                if product_id not in excluded_ids and product_id in self.products:
                    product_scores[product_id] += similarity
        
        # 生成推荐
        for product_id, score in product_scores.items():
            product = self.products[product_id]
            recommendations.append(RecommendationResult(
                product_id=product_id,
                product_name=product.name,
                score=score,
                reason=f"购买了相似商品的用户也购买了这个",
                strategy="collaborative"
            ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_n]
    
    def _popular_recommend(self, top_n: int) -> List[RecommendationResult]:
        """热门商品推荐"""
        recommendations = []
        
        for product_id, product in self.products.items():
            # 综合销量和评分
            popularity_score = (product.sales_count * 0.7 + product.rating * 10 * 0.3)
            
            recommendations.append(RecommendationResult(
                product_id=product_id,
                product_name=product.name,
                score=popularity_score,
                reason=f"热门商品（销量{product.sales_count}，评分{product.rating}）",
                strategy="popular"
            ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_n]
    
    def _hybrid_recommend(
        self,
        profile: UserProfile,
        top_n: int
    ) -> List[RecommendationResult]:
        """混合推荐（结合内容和协同过滤）"""
        # 获取各策略的推荐结果
        content_recs = self._content_based_recommend(profile, top_n * 2)
        collab_recs = self._collaborative_recommend(profile, top_n * 2)
        popular_recs = self._popular_recommend(top_n)
        
        # 合并并重新打分
        combined_scores = defaultdict(lambda: {"score": 0.0, "reasons": [], "product_name": ""})
        
        # 内容推荐（权重 0.5）
        for rec in content_recs:
            combined_scores[rec.product_id]["score"] += rec.score * 0.5
            combined_scores[rec.product_id]["reasons"].append(rec.reason)
            combined_scores[rec.product_id]["product_name"] = rec.product_name
        
        # 协同过滤（权重 0.3）
        for rec in collab_recs:
            combined_scores[rec.product_id]["score"] += rec.score * 0.3
            combined_scores[rec.product_id]["reasons"].append(rec.reason)
            combined_scores[rec.product_id]["product_name"] = rec.product_name
        
        # 热门推荐（权重 0.2）- 只用于补充
        for rec in popular_recs[:3]:  # 只取前3个热门商品
            if rec.product_id not in combined_scores:
                combined_scores[rec.product_id]["score"] += rec.score * 0.2
                combined_scores[rec.product_id]["reasons"].append(rec.reason)
                combined_scores[rec.product_id]["product_name"] = rec.product_name
        
        # 生成最终推荐列表
        recommendations = []
        for product_id, data in combined_scores.items():
            recommendations.append(RecommendationResult(
                product_id=product_id,
                product_name=data["product_name"],
                score=data["score"],
                reason="; ".join(set(data["reasons"])),  # 去重
                strategy="hybrid"
            ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_n]
    
    def get_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像和推荐摘要"""
        profile = self.get_or_create_user_profile(user_id)
        
        return {
            "user_id": user_id,
            "profile": {
                "viewed_count": len(profile.viewed_products),
                "purchased_count": len(profile.purchased_products),
                "searched_keywords": profile.searched_keywords[-10:],  # 最近10次搜索
                "top_categories": profile.get_top_categories(),
                "top_brands": profile.get_top_brands(),
                "price_range": profile.price_range,
                "is_vip": profile.is_vip,
            },
            "recommendations": {
                "content_based": [
                    {"product_id": r.product_id, "score": round(r.score, 2), "reason": r.reason}
                    for r in self._content_based_recommend(profile, 5)
                ],
                "collaborative": [
                    {"product_id": r.product_id, "score": round(r.score, 2), "reason": r.reason}
                    for r in self._collaborative_recommend(profile, 5)
                ],
                "hybrid": [
                    {"product_id": r.product_id, "score": round(r.score, 2), "reason": r.reason}
                    for r in self._hybrid_recommend(profile, 5)
                ],
            }
        }
