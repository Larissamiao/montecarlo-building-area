from functools import partial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import time
from multiprocessing import Pool
import os
from tqdm import tqdm

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def check_in_or_out_circle(x, y):
    return x**2 + y**2 <= 1


def check_in_or_out_building(x, y, domain: Path):
    if isinstance(x, np.ndarray):
        coordinates = np.stack((x, y), axis=-1)
    else:
        coordinates = np.array([[x, y]])
    return domain.contains_points(coordinates)


def mc_slow(n, check_func, approx_func):
    count = 0
    start_time = time.time()
    for _ in tqdm(range(n)):
        x = np.random.uniform(0, 1)
        y = np.random.uniform(0, 1)
        if check_func(x, y):
            count += 1
    pi = approx_func(count, n)
    end_time = time.time()
    return pi, end_time - start_time


def mc_numpy(n, check_func, approx_func):
    start_time = time.time()
    x = np.random.uniform(0, 1, n)
    y = np.random.uniform(0, 1, n)
    dist = check_func(x, y)
    inside = np.sum(dist)
    pi = approx_func(inside, n)
    end_time = time.time()
    return pi, end_time - start_time


def _count_points_worker(n, check_func):
    """Worker function for multiprocess version - counts points inside circle"""
    count = 0
    for _ in range(n):
        x = np.random.uniform(0, 1)
        y = np.random.uniform(0, 1)
        if check_func(x, y):
            count += 1
    return count


def mc_multiprocess(n, num_processes, check_func, approx_func):
    """Multiprocess version of estimate_pi_slow"""

    # Divide work across processes
    samples_per_process = n // num_processes
    remainder = n % num_processes

    # Create sample counts for each process
    sample_counts = [samples_per_process] * num_processes
    # Distribute remainder samples
    for i in range(remainder):
        sample_counts[i] += 1

    start_time = time.time()
    # Run multiprocess calculation
    with Pool(num_processes) as pool:
        counts = pool.starmap(
            _count_points_worker,
            ((count, check_func) for count in sample_counts),
        )

    # Aggregate results
    total_inside = sum(counts)
    pi = approx_func(total_inside, n)
    end_time = time.time()

    return pi, end_time - start_time


def approx_fn(inside, total, ratio):
    return (inside / total) * ratio


def run_experiment(exp_name, sample_sizes):
    print(f"\n{'='*20} 实验: {exp_name} {'='*20}\n")
    print(
        f"{'样本量(N)':<10} | {'循环(s)':<12} | {'多进程(s)':<12} | {'Numpy(s)':<12} | {'估计值':<12}"
    )
    print("-" * 55)

    if exp_name == "建筑面积估计":
        from fp import build_rough_floorplan_domain

        gt_value = 826716508.263378
        domain, bbox_area = build_rough_floorplan_domain()
        check_func = partial(check_in_or_out_building, domain=domain)
        approx_func = partial(approx_fn, ratio=bbox_area)

    elif exp_name == "圆周率估计":
        gt_value = np.pi
        check_func = check_in_or_out_circle
        approx_func = partial(approx_fn, ratio=4)

    approx_values = []
    times_loop = []
    times_mp = []
    times_numpy = []
    NUM_PROCESSES = os.cpu_count() // 2
    for n in sample_sizes:

        pi_loop, t_loop = mc_slow(n, check_func, approx_func)
        pi_mp, t_mp = mc_multiprocess(n, NUM_PROCESSES, check_func, approx_func)
        pi_numpy, t_numpy = mc_numpy(n, check_func, approx_func)

        times_loop.append(t_loop)
        times_mp.append(t_mp)
        times_numpy.append(t_numpy)

        approx_values.append(pi_numpy)
        print(f"{n:<13} | {t_loop:.4f} | {t_mp:.4f} | {t_numpy:.4f} | {pi_numpy:.6f}")
    gen_plots(sample_sizes, times_loop, times_mp, times_numpy, approx_values, gt_value, exp_name)


def gen_plots(sample_sizes, times_loop, times_mp, times_numpy, approx_values, gt_value, exp_name):
    print("\n正在生成图表，请稍候...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    valid_idx = [i for i, t in enumerate(times_loop) if t > 0]
    indices = np.arange(len(valid_idx))
    width = 0.3

    ax1.bar(
        indices - width,
        [times_loop[i] for i in valid_idx],
        width,
        label="传统循环(慢)",
        color="gray",
    )

    ax1.bar(
        indices,
        [times_mp[i] for i in valid_idx],
        width,
        label="多进程循环",
        color="cyan",
    )

    ax1.bar(
        indices + width,
        [times_numpy[i] for i in valid_idx],
        width,
        label="Numpy向量化(快)",
        color="red",
    )
    ax1.set_xticks(indices)
    ax1.set_xticklabels([str(sample_sizes[i]) for i in valid_idx])
    ax1.set_yscale("log")
    ax1.set_ylabel("耗时 (秒, 对数坐标)")
    ax1.set_title("算法效率对比 (越低越好)")
    ax1.legend()

    ax2.plot(sample_sizes, approx_values, "o-", color="blue", label="估计值")
    ax2.axhline(y=gt_value, color="red", linestyle="--", label="真实值")

    ax2.set_xscale("log")
    ax2.set_xlabel("样本量 (对数坐标)")
    ax2.set_ylabel("估计值")
    ax2.set_title("精度收敛趋势")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()

    filename = f"result_{exp_name}.png"
    fig.savefig(filename, dpi=300)

    print(f"\n成功！图片已保存为: {filename}")


if __name__ == "__main__":
    sample_sizes = [1000 * 4**i for i in range(7)]
    # run_experiment("圆周率估计", sample_sizes)
    run_experiment("建筑面积估计", sample_sizes)
