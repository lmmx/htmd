## Small string (12 lines)

Source: `hello_world_x1000`

```sh
bash run_small_benchmark.sh
```

```
Benchmark 1: baseline
  Time (mean ± σ):      62.9 ms ±   1.2 ms    [User: 56.6 ms, System: 6.9 ms]
  Range (min … max):    61.8 ms …  66.2 ms    46 runs

Benchmark 2: markdownify
  Time (mean ± σ):      1.736 s ±  0.026 s    [User: 1.711 s, System: 0.024 s]
  Range (min … max):    1.705 s …  1.777 s    10 runs

Summary
  'baseline' ran
   27.62 ± 0.66 times faster than 'markdownify'
```

## Medium file (1000 lines)

Source: `turndown_test_index_x10`

```sh
bash run_medium_benchmark.sh
```

```
Benchmark 1: baseline
  Time (mean ± σ):     109.0 ms ±   1.6 ms    [User: 94.3 ms, System: 14.5 ms]
  Range (min … max):   107.1 ms … 113.7 ms    27 runs

Benchmark 2: markdownify
  Time (mean ± σ):      1.042 s ±  0.006 s    [User: 1.012 s, System: 0.029 s]
  Range (min … max):    1.035 s …  1.051 s    10 runs

Summary
  'baseline' ran
    9.56 ± 0.15 times faster than 'markdownify'
```
