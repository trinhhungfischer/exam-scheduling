# Mô hình hóa bài toán
Sẽ có các biến sau đây trong bài toán Constraints Programming

Chúng ta sẽ có các biến sau đây
- $x[i]$ thể hiện kíp thi cho môn $i$ trong đó $i \in \{0,...,N-1\},\  D(x[i])=\{0,...,N-1\}$
- $y[i][j]$ thể hiện môn $i$ được xếp vào phòng $j$ trong đó $i \in \{0,...,N-1\}, j \in \{0,...,M-1\}, D(y[i][j])=\{0,1\}$
- Gọi $C$ là tập các môn học $(i, j)$ mà không thể xếp cùng kíp.

Mục tiêu của bài toán là minimize $max(x) \rightarrow min$.

Chúng ta có các rằng buộc gốc cho bài toán như sau

1. Hai môn cùng kíp thi không được xếp cùng phòng
$$ \forall i1,i2 \in {1,...,N}, j \in {1,...,M}, x[i1]=x[i2] \Rightarrow y[i1][j] + y[i2][j] \le 1 $$
2. Mỗi phòng chỉ có thể được xếp tối đa 1 môn trong 1 kíp
$$\sum_{j=0}^{M-1} y[i][j]=1; \forall i \in \{1,...,N\}$$
1. Xếp các môn thi $i$ vào phòng thi $j$ có sức chưa $c[j]$ phù hợp:
$$\sum_{k=0}^{M-1} y[i][j] * c[i] \ge d[j]; \ \ \ \forall \ i=0...M-1$$
1. Hai môn thi conflict với nhau không thể xếp cùng 1 kíp
$$\forall(i,j) \in C \Rightarrow x[i] \neq x[j[$$
Ngoài ra chúng ta có rằng buộc cho biến mục tiêu
$$x[i][j][k] * k <= y; \forall j=0...M-1; i,k=0...N-1$$
