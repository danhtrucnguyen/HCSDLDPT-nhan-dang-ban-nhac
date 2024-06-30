import math
import jsonpickle as json
import TrichRutDacTrung
from Class import Cluster
from collections import Counter
import pandas as pd


def SimilarityCalculation(clusters, features):  #features là list các đặc trưng 
    labelCount = []
    for feature in features:
        dmin = 9999999999999999.9
        tmp = 0
        for c in range(len(clusters)):
            d = euclideanDistance(clusters[c].center, feature)
            if(d < dmin):
                dmin = d
                tmp = c
        count = []
        lb = []
        for i in range(1):
            count.append(9999999999999999.9)
            lb.append("")
        for f in clusters[tmp].features:
            d = euclideanDistance(feature, f.feature)

            # Thêm điều kiện nếu d > ngưỡng thì loại f
            if(d > 5000):
                continue

            for i in range(1):
                if(count[i] > d):
                    count[i] = d
                    lb[i] = f.link
                    break

        for i in range(1):
            if(lb[i] != ""):
                labelCount.append((lb[i], count[i]))
        # # Đếm số lần xuất hiện của các link trong labelCount
        # link_counts = Counter(labelCount)
        #  # Lấy ra 3 link có số lần xuất hiện nhiều nhất
        # top_3_links = [link for link, _ in link_counts.most_common(3)]
     # Tạo DataFrame từ link_counts
    df = pd.DataFrame(labelCount, columns=['f_link', 'count'])

    # Tính trung bình count theo từng f.link
    mean_counts = df.groupby('f_link')['count'].mean()

    # Lấy ra 3 f.link có trung bình count thấp nhất
    top_3_links = mean_counts.nsmallest(3).index.tolist()
    return top_3_links

def euclideanDistance(feature1, feature2):
    squared_difference = 0.0
    for i in range(len(feature1)):
        squared_difference += (feature1[i] - feature2[i]) ** 2
    squared_difference = math.sqrt(squared_difference)
    return math.sqrt(squared_difference)


