# CodeReviewAgent 修复说明

## 本次修改

1. 将评测指标计算从 `run_eval.py` 拆到 `src/metrics.py`，使其不需要导入模型客户端即可独立测试。
2. 修正 `strict_precision`：分子为正例案例中、通过证据校验且 `issue_type` 与期望类型匹配的 finding 数；分母为所有通过证据校验的 finding 数（包含干净案例误报和类型不匹配的 finding）。无有效 finding 时返回 `null`（Python 中为 `None`）。
3. `strict_recall` 仍按案例计算：正例案例中至少有一个有效且类型匹配 finding 的案例数 / 正例案例总数。
4. 更新输出 JSON 的 `metrics_definition`，明确基础分类指标按案例计算、严格精确率按 finding 计算。
5. 新增 `tests/test_metrics.py`，覆盖严格指标分母/分子口径及空数据集边界情况。

## 验证结果

- `python -m py_compile run_eval.py src/metrics.py`：通过。
- `python -m unittest tests.test_metrics -v`：2 项通过。
- 在本次 Linux 隔离环境执行完整测试时，除 reviewer 集成测试无法导入外，其余 27 项通过。失败原因是当前执行环境没有可用的 `openai` 依赖；尝试复用压缩包内 Windows `.venv` 也因 Windows 编译扩展无法在 Linux 环境加载而失败。这不是对用户 Windows 环境测试结果的判断。
- 本次没有发起任何真实模型 API 调用，因此没有产生本次修复验证所需的 API 请求。

## 未做的事 / 注意事项

- 没有覆盖原来的 `eval_results.json`，也没有把旧结果伪装成新指标结果。
- 没有修改模型提示词、证据校验规则、数据集或 API Key 配置。
- 需要在用户的 Windows 项目虚拟环境中重新执行完整测试；通过后再运行 15 个案例的真实 API 评测。
