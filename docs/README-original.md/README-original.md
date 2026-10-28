## 两个python文件需要放在同一个文件夹中！！！

* `MonteCarlo_Pi_Research.py`主函数
* `fp.py`定义几何形状

### 这个程序（大概率）不会“假死”，没反应只是还在运行

## 估算任意新图形面积
1. 在`fp.py`中定义端点坐标 (变量`VERTICES`, 端点示例参见“新图坐标示意.png”)
2. 在`fp.py`中定义端点间为直线或曲线 （变量`CODES`，每个曲线CURVE4需重复出现3次（3次CURVE4代表一个曲线段））
3. 运行`fp.py`中的 `insert_control_points` 函数 (使曲线平滑连接)
4. 在`MonteCarlo_Pi_Research.py`中定义真实面积（目标值， 变量`gt_value`）
