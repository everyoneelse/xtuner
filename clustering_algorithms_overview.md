# 业界经典聚类算法分类

## 1. 层次聚类 (Hierarchical Clustering)

### 1.1 凝聚层次聚类 (Agglomerative - 自底向上)

| 算法 | Linkage类型 | 特点 | 适用场景 | 时间复杂度 |
|------|------------|------|---------|-----------|
| **Single-linkage** | 最小距离 | 链式效应严重，容易产生长条形cluster | 发现不规则形状的cluster | O(n²) |
| **Complete-linkage** | 最大距离 | cluster最紧凑，但可能过度分割 | 紧凑型、球形cluster | O(n²) |
| **Average-linkage (UPGMA)** | 平均距离 | **最常用**，平衡效果好 | 通用场景 | O(n²) |
| **Ward's method** | 方差最小化 | sklearn默认，最小化cluster内方差 | 大小相近的球形cluster | O(n²) |

```python
from sklearn.cluster import AgglomerativeClustering

# Ward's method (默认)
model = AgglomerativeClustering(n_clusters=3, linkage='ward')

# Average-linkage
model = AgglomerativeClustering(n_clusters=3, linkage='average')

# Complete-linkage
model = AgglomerativeClustering(n_clusters=3, linkage='complete')

# Single-linkage
model = AgglomerativeClustering(n_clusters=3, linkage='single')
```

### 1.2 分裂层次聚类 (Divisive - 自顶向下)
- 从一个大cluster开始，递归分割
- DIANA (Divisive Analysis)
- 较少使用，计算复杂度高

---

## 2. 基于划分的聚类 (Partitioning / Centroid-based)

### 2.1 K-Means
- **类型**: Centroid-based
- **原理**: 迭代优化，最小化点到中心的距离平方和
- **优点**: 快速、简单、可扩展
- **缺点**: 需要预设k，对初始值敏感，只能发现球形cluster
- **时间复杂度**: O(n·k·i) (i为迭代次数)

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, init='k-means++', n_init=10)
labels = kmeans.fit_predict(X)
```

### 2.2 K-Medoids (PAM - Partitioning Around Medoids)
- **类型**: Medoid-based (使用实际数据点作为中心)
- **优点**: 对异常值更鲁棒，支持任意距离度量
- **缺点**: 比K-Means慢
- **时间复杂度**: O(n²)

```python
from sklearn_extra.cluster import KMedoids

kmedoids = KMedoids(n_clusters=3, metric='euclidean')
labels = kmedoids.fit_predict(X)
```

### 2.3 K-Modes / K-Prototypes
- **K-Modes**: 用于分类数据
- **K-Prototypes**: 用于混合数据（数值+分类）

---

## 3. 基于密度的聚类 (Density-based)

### 3.1 DBSCAN (Density-Based Spatial Clustering)
- **类型**: Density-based
- **原理**: 基于密度可达性，连接高密度区域
- **优点**: 
  - 可发现任意形状的cluster
  - 自动识别噪声点
  - 不需要预设cluster数量
- **缺点**: 
  - 对参数敏感 (eps, min_samples)
  - 难以处理密度差异大的数据
- **时间复杂度**: O(n log n) with spatial index

```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X)
# 噪声点标记为 -1
```

### 3.2 HDBSCAN (Hierarchical DBSCAN)
- **改进**: 自动选择eps，处理变密度cluster
- **推荐**: 通常比DBSCAN更好用

```python
import hdbscan

clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=1)
labels = clusterer.fit_predict(X)
```

### 3.3 OPTICS
- **原理**: 生成可达性图，类似DBSCAN但更灵活
- **优点**: 可以发现不同密度的cluster

---

## 4. 基于分布的聚类 (Distribution-based)

### 4.1 Gaussian Mixture Model (GMM)
- **类型**: 概率模型，基于EM算法
- **原理**: 假设数据由多个高斯分布混合生成
- **优点**: 
  - 提供概率归属（soft clustering）
  - 可以有overlap的cluster
  - 可以建模elliptical clusters
- **缺点**: 假设数据分布，可能不适用

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=3, covariance_type='full')
labels = gmm.fit_predict(X)
probabilities = gmm.predict_proba(X)  # soft clustering
```

---

## 5. 基于图的聚类 (Graph-based)

### 5.1 Spectral Clustering
- **类型**: Graph-based
- **原理**: 构建相似度图 → 图分割 (基于特征值分解)
- **优点**: 可以发现非凸形状的cluster
- **缺点**: 计算复杂度高，需要预设k
- **时间复杂度**: O(n³) (特征值分解)

```python
from sklearn.cluster import SpectralClustering

spectral = SpectralClustering(n_clusters=3, affinity='nearest_neighbors')
labels = spectral.fit_predict(X)
```

### 5.2 Affinity Propagation
- **类型**: Message-passing
- **原理**: 数据点间传递消息，选举exemplars
- **优点**: 自动确定cluster数量
- **缺点**: O(n²) 时间和空间复杂度，参数难调

```python
from sklearn.cluster import AffinityPropagation

ap = AffinityPropagation(damping=0.9, preference=-50)
labels = ap.fit_predict(X)
```

---

## 6. 特殊用途聚类

### 6.1 Mean Shift
- **类型**: Centroid-based，滑动窗口
- **优点**: 自动确定cluster数量，可发现任意形状
- **缺点**: 计算慢，对bandwidth参数敏感

```python
from sklearn.cluster import MeanShift

ms = MeanShift(bandwidth=2.0)
labels = ms.fit_predict(X)
```

### 6.2 BIRCH (Balanced Iterative Reducing and Clustering)
- **类型**: Hierarchical + Centroid-based
- **优点**: 适合大规模数据，增量式
- **时间复杂度**: O(n)

```python
from sklearn.cluster import Birch

birch = Birch(n_clusters=3, threshold=0.5)
labels = birch.fit_predict(X)
```

---

## 算法选择指南

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| **球形、大小相近的cluster** | K-Means, Ward's | 快速高效 |
| **任意形状的cluster** | DBSCAN, HDBSCAN, Spectral | 不假设形状 |
| **不知道cluster数量** | DBSCAN, HDBSCAN, Affinity Propagation | 自动确定 |
| **有噪声点/异常值** | DBSCAN, HDBSCAN, K-Medoids | 鲁棒性好 |
| **需要层次结构** | Agglomerative Clustering | 生成dendrogram |
| **需要soft clustering** | GMM | 提供概率 |
| **大规模数据** | Mini-Batch K-Means, BIRCH | 可扩展 |
| **高维数据** | Spectral Clustering | 降维效果 |
| **文本/稀疏数据** | K-Means (with cosine), Agglomerative | 支持自定义距离 |

---

## 对你的场景的建议

根据你之前提到的 **候选项聚类** 场景：

### 如果是embedding聚类（向量）：
```python
# 方案1: HDBSCAN (推荐)
import hdbscan
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,      # 最小cluster大小
    min_samples=1,           # 核心点的邻域大小
    metric='cosine',         # 余弦相似度
    cluster_selection_epsilon=0.2  # 合并阈值
)
labels = clusterer.fit_predict(embeddings)

# 方案2: Agglomerative + Average-linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# 预计算相似度矩阵
similarity_matrix = cosine_similarity(embeddings)
distance_matrix = 1 - similarity_matrix

clusterer = AgglomerativeClustering(
    n_clusters=None,         # 不固定数量
    distance_threshold=0.3,  # 距离阈值 (1-相似度阈值)
    linkage='average',       # 平均链接
    metric='precomputed'
)
labels = clusterer.fit_predict(distance_matrix)
```

### 如果是在线/增量场景：
```python
# 自定义增量聚类（使用average-linkage策略）
class IncrementalClusterer:
    def __init__(self, threshold=0.8, linkage='average'):
        self.clusters = []  # List[List[int]]，存储索引
        self.embeddings = []
        self.threshold = threshold
        self.linkage = linkage
    
    def add_item(self, embedding):
        idx = len(self.embeddings)
        self.embeddings.append(embedding)
        
        # 找到匹配的clusters
        matching_clusters = []
        for cluster_idx, cluster in enumerate(self.clusters):
            if self._should_join(embedding, cluster):
                matching_clusters.append(cluster_idx)
        
        if len(matching_clusters) == 0:
            # 创建新cluster
            self.clusters.append([idx])
        elif len(matching_clusters) == 1:
            # 加入唯一匹配的cluster
            self.clusters[matching_clusters[0]].append(idx)
        else:
            # 合并多个匹配的clusters
            merged = [idx]
            for cluster_idx in sorted(matching_clusters, reverse=True):
                merged.extend(self.clusters[cluster_idx])
                del self.clusters[cluster_idx]
            self.clusters.append(merged)
    
    def _should_join(self, embedding, cluster):
        if self.linkage == 'average':
            # Average-linkage
            similarities = [
                cosine_similarity([embedding], [self.embeddings[i]])[0][0]
                for i in cluster
            ]
            return np.mean(similarities) > self.threshold
        elif self.linkage == 'complete':
            # Complete-linkage
            similarities = [
                cosine_similarity([embedding], [self.embeddings[i]])[0][0]
                for i in cluster
            ]
            return min(similarities) > self.threshold
        elif self.linkage == 'single':
            # Single-linkage (不推荐)
            similarities = [
                cosine_similarity([embedding], [self.embeddings[i]])[0][0]
                for i in cluster
            ]
            return max(similarities) > self.threshold
```

## 实践建议

1. **先试HDBSCAN**: 对大多数场景效果好，参数少
2. **需要可解释性用Agglomerative**: 可以画dendrogram
3. **大规模数据用K-Means变体**: 速度快
4. **不确定就用Average-linkage**: 经典且平衡

你的场景具体是什么？我可以给出更针对性的建议。
