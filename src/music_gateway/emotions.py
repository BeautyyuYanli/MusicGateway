from typing import List

import numpy as np

from music_gateway.emb_model import clap_emb_model

emotions = [
    "happy",
    "sad",
    "angry",
    "calm",
    "peaceful",
    "energetic",
    "hopeful",
    "nostalgic",
    "dreamy",
    "playful",
    "funny",
    "romantic",
    "heartbroken",
    "lonely",
    "inspired",
    "thoughtful",
    "confusing",
    "scary",
    "tense",
    "mysterious",
    "triumphant",
    "celebratory",
]

texts_data = [f"This audio is a {emotion} song" for emotion in emotions]
texts_embed = clap_emb_model.emb_texts(texts_data)
emotions_with_embed = list(zip(emotions, texts_embed, strict=False))


def k_means_clustering(data_list, num_clusters=2, tolerance=1e-4):
    """
    简化的K-Means聚类算法。

    参数:
    - data_list: List[np.ndarray]，输入的数据点列表。
    - num_clusters: int，指定要分成的聚类数量，默认为2。

    返回:
    - List[np.ndarray]，聚类后的数据点列表。
    """
    # 将输入的数据点列表转换为一个大的numpy数组，以便进行向量化操作
    data = np.vstack(data_list)

    # 随机初始化聚类中心
    centroids = data[np.random.choice(data.shape[0], num_clusters, replace=False), :]

    while True:
        # 计算每个数据点到各个聚类中心的距离
        distances = np.sqrt(((data - centroids[:, np.newaxis]) ** 2).sum(axis=2))

        # 为每个数据点分配最近的聚类中心
        closest_centroids = np.argmin(distances, axis=0)

        prev_centroids = centroids.copy()
        # 更新聚类中心
        for i in range(num_clusters):
            centroids[i] = data[closest_centroids == i].mean(axis=0)

        if np.max(np.sqrt((centroids - prev_centroids) ** 2).sum(axis=1)) < tolerance:
            break

    # 根据最终的聚类中心，重新分配数据点
    cluster_assignments = np.argmin(
        np.sqrt(((data - centroids[:, np.newaxis]) ** 2).sum(axis=2)), axis=0
    )

    # 将数据点按照聚类结果组织成列表
    clustered_data = [data[cluster_assignments == i] for i in range(num_clusters)]

    return clustered_data


def get_emotion_by_emb(emb: np.ndarray) -> List[str]:
    distances = [np.linalg.norm(text_embed - emb) for text_embed in texts_embed]
    scores = [
        1 - ((dis - min(distances)) / (max(distances) - min(distances)))
        for dis in distances
    ]
    emotion_with_embed_with_score = [
        (*emotions_with_embed[i], score)
        for i, score in enumerate(scores)
        if score > 0.65
    ]
    if len(emotion_with_embed_with_score) <= 3:
        return [x[0] for x in emotion_with_embed_with_score]
    clusters = k_means_clustering([x[1] for x in emotion_with_embed_with_score], 2)

    emotions_grouped_with_score = [
        [x for x in emotion_with_embed_with_score if x[1] in cluster]
        for cluster in clusters
    ]
    group_with_score = [
        ([x[0] for x in group], np.average([x[2] for x in group]))
        for group in emotions_grouped_with_score
    ]
    group_with_score.sort(key=lambda x: x[1], reverse=True)
    return group_with_score[0][0]


if __name__ == "__main__":
    # From audio files
    audios_file = [
        "tests/data/WhiteNight.webm",
        "tests/data/FocalorsSacrifice.webm",
    ]
    audios_embed = clap_emb_model.emb_audios(audios_file)
    for embed in audios_embed:
        print(get_emotion_by_emb(embed))
