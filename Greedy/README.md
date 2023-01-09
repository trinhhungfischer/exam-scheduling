# Mô hình hóa bài toán

Sẽ có các biến sau đây trong bài toán Mixed Integer Programming

- $x[i][j][k]$ là biến nhị phân xếp môn $i$ vào phòng thứ $j$ tại kíp thứ $k$ trong đó $i,k \in \{0,...,N-1\}$ và $j \in \{0,...,M-1\}$

- $y$ là số kíp thi $D(y) = \{0, 1, ..., N-1\}$.

- Gọi $C$ là tập các môn học $(i, j)$ mà không thể xếp cùng kíp.

Mục tiêu của bài toán là minimize $y$.

Chúng ta có các rằng buộc gốc cho bài toán như sau

1. Mỗi môn đều được xếp lịch thi duy nhất 1 lần vào 1 phòng
$$\sum_{k=0}^{N-1} \sum_{j=0}^{M-1} x[i][j][k] = 1 \ \ \ \forall \ i= 0...N-1$$
2. Mỗi phòng chỉ có thể được xếp tối đa 1 môn trong 1 kíp
$$\sum_{i=0}^{N-1} x[i][j][k] \le 1 \ \ \ \forall \ k=0...N-1; \ j=0...M-1$$
3. Xếp các môn thi $i$ vào phòng thi $j$ có sức chưa $c[j]$ phù hợp:
$$\sum_{k=0}^{N-1} x[i][j][k] * d[i] \le c[j] \ \ \ \forall \ i=0...N-1; \ j=0...M-1$$
4. Hai môn thi conflict với nhau không thể xếp cùng 1 kíp
$$\sum_{j=0}^{M-1} (x[i1][j][k] + x[i2][j][k]) \le 1 \ \ \ \forall \ k=0...N-1; \ (i1, i2) \in C$$
Ngoài ra chúng ta có rằng buộc cho biến mục tiêu
$$x[i][j][k] * k \le y \forall j=0...M-1; i,k=0...N-1$$
