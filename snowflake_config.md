# Snowflake 数据层与 Cortex 配置验证

实测时间（UTC）：2026-10-14T15:49:36.915006+00:00 至 2026-10-14T15:50:41.948309+00:00。

**结果：连接、全部 73 个对象的读取计数、核心 schema 和三个 Cortex 模型调用均成功；最后一次元数据检查后仓库已确认 SUSPENDED。**
这是一轮真实远程配置 smoke test，不代表聊天 agent 已实现或通过准确性评估。

## 连接参数

| 参数 | 值 |
| --- | --- |
| Account / connector account | ssybhom-kx56542 |
| CURRENT_ACCOUNT() | GA75621 |
| User | CODEX_APP |
| Password | 见 .env（不提交） |
| 当前 Role | PUBLIC |
| Warehouse | SNOWFLAKE_LEARNING_WH |
| Database | US_OPEN_CENSUS_DATA_NEIGHBORHOOD_INSIGHTS_FREE_DATASET |
| Schema | PUBLIC |
| 实测 CURRENT_REGION() | AWS_CA_CENTRAL_1 |
| Connector | 4.8.0 |
| 本地默认 Cortex 模型 | llama3.1-70b（SNOWFLAKE_CORTEX_MODEL） |

**区域差异：提供信息称 AWS us-east-1；实际 CURRENT_REGION() 返回 AWS_CA_CENTRAL_1。使用账户标识连接已成功；不要硬编码 us-east-1 endpoint。**

`.env` 已被 `.gitignore` 排除，权限为 600。连接代码只读取所需连接键，凭证不进入报告或 JSON 证据。

```bash
.venv/bin/python -m pip install -r requirements-dev.txt -r requirements-snowflake.txt
.venv/bin/python scripts/snowflake_probe.py --mode inventory --output docs/snowflake_inventory.json
.venv/bin/python scripts/snowflake_probe.py --mode full \
  --core-table 2020_CBG_B01 \
  --core-table 2020_REDISTRICTING_CBG_DATA \
  --core-table 2020_METADATA_CBG_GEOGRAPHIC_DATA
```

这些命令会连接远程、可能消耗 credit；full 模式会重新计数并重新调用模型。默认读取 repo 根目录 `.env`，不向 shell source 该文件。

## Cortex 实测

通过 connector 执行 `SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)`，参数为模型名和 `Say hello in one sentence.`。绑定参数与指定 literal 查询语义相同。

| 模型 | 结果 | 客户端耗时（秒） | 返回/失败原因 | Query ID |
| --- | --- | --- | --- | --- |
| llama3.1-70b | 可用 | 0.741 | Hello, it's nice to meet you! | 01c7ba36-3204-bd12-0008-3d1a000165be |
| llama3.3-70b | 可用 | 1.875 | Hello, it's nice to meet you and I'm here to help with any questions or topics you'd like to discuss! | 01c7ba36-3204-bd57-0008-3d1a000175be |
| mistral-7b | 可用 | 0.746 |  Hello there! I'm an assistant here to help answer any questions you might have. How may I assist you today? | 01c7ba36-3204-bd57-0008-3d1a000175c2 |
| gemma2-9b | 不可用 | 20.953 | 512513 (P0000): Request failed for external function COMPLETE with remote service error: '400 'unknown model "gemma2-9b"''; requests batch-id: 01c7ba36-3204-bb79-0008-3d1a00015772-0; request batch size: 1 rows; request retries: 0; response time (last retry): 0 | 01c7ba36-3204-bb79-0008-3d1a00015772 |

- 实测可用清单：`llama3.1-70b`、`llama3.3-70b`、`mistral-7b`。
- `gemma2-9b` 返回 `unknown model`（errno 512513）；20.953 秒是失败请求耗时，不是成功推理延迟。
- 按用户要求，未调用 `mistral-large` 或 `mistral-large2`。
- 每个模型只调用一次；耗时包含 connector 请求与取回结果，不是平均值、p95、纯模型延迟或质量比较。未测 token/credit 账单。
- 连通性通过不代表严格遵守提示：`mistral-7b` 在这次测试中返回多句话。
- 官方文档将 COMPLETE 定位为兼容接口，并建议新用例考虑 AI_COMPLETE；本次按要求只验证 COMPLETE，未实测 AI_COMPLETE。
  参见 [Snowflake COMPLETE 文档](https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex)。

## 全部对象：名称 → 实测行数 → 描述

`SHOW TABLES` 返回 71 张表，`SHOW VIEWS` 返回 2 个视图，合计 73 个可查询对象。每个计数都实际执行了 `SELECT COUNT(*)`，没有用 SHOW 的 rows 字段替代。

B/C 主题描述参考实测 2020 字段字典；2019 同代码主题沿用该解释，未逐列核对 2019 字典。名称推断或未核实内容已标明。

| 对象名（精确大小写） | 类型 | COUNT(*) | 一句话描述 |
| --- | --- | --- | --- |
| 2019_CBG_B01 | TABLE | 220333 | 2019 年 CBG 层级；人口总量、性别、年龄分布及年龄中位数的估计值和误差。 |
| 2019_CBG_B02 | TABLE | 220333 | 2019 年 CBG 层级；种族构成与相关细分人口指标。 |
| 2019_CBG_B03 | TABLE | 220333 | 2019 年 CBG 层级；西班牙裔/拉丁裔身份及其种族构成。 |
| 2019_CBG_B07 | TABLE | 220333 | 2019 年 CBG 层级；居住迁移与过去居住地点相关指标。 |
| 2019_CBG_B08 | TABLE | 220333 | 2019 年 CBG 层级；通勤方式、时间及相关人口指标。 |
| 2019_CBG_B09 | TABLE | 220333 | 2019 年 CBG 层级；儿童、家庭关系与家庭成员结构相关指标。 |
| 2019_CBG_B11 | TABLE | 220333 | 2019 年 CBG 层级；住户/家庭类型、规模及相关人口指标。 |
| 2019_CBG_B12 | TABLE | 220333 | 2019 年 CBG 层级；婚姻状况和婚姻历史相关人口指标。 |
| 2019_CBG_B14 | TABLE | 220333 | 2019 年 CBG 层级；学校就读、入学情况与学校类型相关指标。 |
| 2019_CBG_B15 | TABLE | 220333 | 2019 年 CBG 层级；教育程度及其人口细分指标。 |
| 2019_CBG_B16 | TABLE | 220333 | 2019 年 CBG 层级；家庭语言及英语能力相关指标。 |
| 2019_CBG_B17 | TABLE | 220333 | 2019 年 CBG 层级；贫困状态及其人口细分指标。 |
| 2019_CBG_B19 | TABLE | 220333 | 2019 年 CBG 层级；住户、家庭及个人收入相关指标。 |
| 2019_CBG_B20 | TABLE | 220333 | 2019 年 CBG 层级；劳动收入及性别、工作经历细分指标。 |
| 2019_CBG_B21 | TABLE | 220333 | 2019 年 CBG 层级；退伍军人身份及相关人口指标。 |
| 2019_CBG_B22 | TABLE | 220333 | 2019 年 CBG 层级；食品券/SNAP 领取与住户残障状态相关指标。 |
| 2019_CBG_B23 | TABLE | 220333 | 2019 年 CBG 层级；就业、劳动力状态与工作经历相关指标。 |
| 2019_CBG_B24 | TABLE | 220333 | 2019 年 CBG 层级；职业、行业及其人口细分指标。 |
| 2019_CBG_B25 | TABLE | 220333 | 2019 年 CBG 层级；住房、产权/租赁、费用与住房条件相关指标。 |
| 2019_CBG_B27 | TABLE | 220333 | 2019 年 CBG 层级；医疗保险覆盖及其人口细分指标。 |
| 2019_CBG_B28 | TABLE | 220333 | 2019 年 CBG 层级；计算机、互联网及相关家庭接入指标。 |
| 2019_CBG_B29 | TABLE | 220333 | 2019 年 CBG 层级；有投票年龄的公民人口及其相关指标。 |
| 2019_CBG_B99 | TABLE | 220333 | 2019 年 CBG 层级；调查字段 allocation/填补相关指标。 |
| 2019_CBG_C02 | TABLE | 220333 | 2019 年 CBG 层级；种族构成的 C 系列汇总指标。 |
| 2019_CBG_C15 | TABLE | 220333 | 2019 年 CBG 层级；教育程度的 C 系列汇总指标。 |
| 2019_CBG_C16 | TABLE | 220333 | 2019 年 CBG 层级；家庭语言的 C 系列汇总指标。 |
| 2019_CBG_C17 | TABLE | 220333 | 2019 年 CBG 层级；贫困与收入的 C 系列汇总指标。 |
| 2019_CBG_C21 | TABLE | 220333 | 2019 年 CBG 层级；退伍军人、残障与贫困的 C 系列相关指标。 |
| 2019_CBG_C24 | TABLE | 220333 | 2019 年 CBG 层级；职业和行业的 C 系列汇总指标。 |
| 2019_CBG_GEOMETRY | TABLE | 220740 | CBG 边界几何数据；具体类型/编码需查询对应 schema。 |
| 2019_CBG_GEOMETRY_WKT | TABLE | 220740 | CBG 边界几何数据，表注释说明为 WKT 文本。 |
| 2019_CBG_PATTERNS | TABLE | 220735 | 名称指向 CBG patterns 数据；仅完成计数，内容含义待提供商说明。 |
| 2019_METADATA_CBG_FIELD_DESCRIPTIONS | TABLE | 8120 | 字段字典：变量 ID、原始表号、主题、统计范围及分层含义。 |
| 2019_METADATA_CBG_FIPS_CODES | TABLE | 3233 | 州/县 FIPS 编码与州缩写、县名、分类代码的映射。 |
| 2019_METADATA_CBG_GEOGRAPHIC_DATA | TABLE | 220333 | CBG 关联的土地/水域面积与经纬度；面积单位尚未确认。 |
| 2019_RENT_PERCENTAGE_HOUSEHOLD_INCOME | VIEW | 220333 | 租金占住户收入比例相关视图；仅完成计数，公式未检查。 |
| 2019_TOTAL_RENTAL_GEO | VIEW | 162721 | 租赁与地理信息相关视图；仅完成计数，视图逻辑未检查。 |
| 2020_CBG_B01 | TABLE | 242335 | 2020 年 CBG 层级；人口总量、性别、年龄分布及年龄中位数的估计值和误差。 |
| 2020_CBG_B02 | TABLE | 242335 | 2020 年 CBG 层级；种族构成与相关细分人口指标。 |
| 2020_CBG_B03 | TABLE | 242335 | 2020 年 CBG 层级；西班牙裔/拉丁裔身份及其种族构成。 |
| 2020_CBG_B07 | TABLE | 242335 | 2020 年 CBG 层级；居住迁移与过去居住地点相关指标。 |
| 2020_CBG_B08 | TABLE | 242335 | 2020 年 CBG 层级；通勤方式、时间及相关人口指标。 |
| 2020_CBG_B09 | TABLE | 242335 | 2020 年 CBG 层级；儿童、家庭关系与家庭成员结构相关指标。 |
| 2020_CBG_B11 | TABLE | 242335 | 2020 年 CBG 层级；住户/家庭类型、规模及相关人口指标。 |
| 2020_CBG_B12 | TABLE | 242335 | 2020 年 CBG 层级；婚姻状况和婚姻历史相关人口指标。 |
| 2020_CBG_B14 | TABLE | 242335 | 2020 年 CBG 层级；学校就读、入学情况与学校类型相关指标。 |
| 2020_CBG_B15 | TABLE | 242335 | 2020 年 CBG 层级；教育程度及其人口细分指标。 |
| 2020_CBG_B16 | TABLE | 242335 | 2020 年 CBG 层级；家庭语言及英语能力相关指标。 |
| 2020_CBG_B17 | TABLE | 242335 | 2020 年 CBG 层级；贫困状态及其人口细分指标。 |
| 2020_CBG_B19 | TABLE | 242335 | 2020 年 CBG 层级；住户、家庭及个人收入相关指标。 |
| 2020_CBG_B20 | TABLE | 242335 | 2020 年 CBG 层级；劳动收入及性别、工作经历细分指标。 |
| 2020_CBG_B21 | TABLE | 242335 | 2020 年 CBG 层级；退伍军人身份及相关人口指标。 |
| 2020_CBG_B22 | TABLE | 242335 | 2020 年 CBG 层级；食品券/SNAP 领取与住户残障状态相关指标。 |
| 2020_CBG_B23 | TABLE | 242335 | 2020 年 CBG 层级；就业、劳动力状态与工作经历相关指标。 |
| 2020_CBG_B24 | TABLE | 242335 | 2020 年 CBG 层级；职业、行业及其人口细分指标。 |
| 2020_CBG_B25 | TABLE | 242335 | 2020 年 CBG 层级；住房、产权/租赁、费用与住房条件相关指标。 |
| 2020_CBG_B27 | TABLE | 242335 | 2020 年 CBG 层级；医疗保险覆盖及其人口细分指标。 |
| 2020_CBG_B28 | TABLE | 242335 | 2020 年 CBG 层级；计算机、互联网及相关家庭接入指标。 |
| 2020_CBG_B29 | TABLE | 242335 | 2020 年 CBG 层级；有投票年龄的公民人口及其相关指标。 |
| 2020_CBG_B99 | TABLE | 242335 | 2020 年 CBG 层级；调查字段 allocation/填补相关指标。 |
| 2020_CBG_C02 | TABLE | 242335 | 2020 年 CBG 层级；种族构成的 C 系列汇总指标。 |
| 2020_CBG_C15 | TABLE | 242335 | 2020 年 CBG 层级；教育程度的 C 系列汇总指标。 |
| 2020_CBG_C16 | TABLE | 242335 | 2020 年 CBG 层级；家庭语言的 C 系列汇总指标。 |
| 2020_CBG_C17 | TABLE | 242335 | 2020 年 CBG 层级；贫困与收入的 C 系列汇总指标。 |
| 2020_CBG_C21 | TABLE | 242335 | 2020 年 CBG 层级；退伍军人、残障与贫困的 C 系列相关指标。 |
| 2020_CBG_C24 | TABLE | 242335 | 2020 年 CBG 层级；职业和行业的 C 系列汇总指标。 |
| 2020_CBG_GEOMETRY_WKT | TABLE | 242335 | CBG 边界几何数据；具体类型/编码需查询对应 schema。 |
| 2020_METADATA_CBG_FIELD_DESCRIPTIONS | TABLE | 8164 | 字段字典：变量 ID、原始表号、主题、统计范围及分层含义。 |
| 2020_METADATA_CBG_FIPS_CODES | TABLE | 3234 | 州/县 FIPS 编码与州缩写、县名、分类代码的映射。 |
| 2020_METADATA_CBG_GEOGRAPHIC_DATA | TABLE | 242335 | CBG 关联的土地/水域面积与经纬度；面积单位尚未确认。 |
| 2020_REDISTRICTING_CBG_DATA | TABLE | 242335 | 2020 年重划选区人口、种族、投票年龄及住房统计。 |
| 2020_REDISTRICTING_METADATA_CBG_FIELD_DESCRIPTIONS | TABLE | 298 | 重划选区字段 ID、字段含义、主题和统计范围的字典。 |
| 2020_REDISTRICTING_METADATA_CBG_GEOGRAPHIC_DATA | TABLE | 242335 | 重划选区 CBG 对应地理元数据；未抽样核实各列含义。 |

## 核心表完整 schema 与样例

下列全部列名和类型来自 `DESCRIBE TABLE`，顺序与 `SELECT * LIMIT 5` 返回一致。标识符必须保留精确大小写并用双引号。五行完整样例已保存于 `docs/snowflake_evidence.json`；下方展示其中重要字段。`LIMIT 5` 没有 ORDER BY，下次抽样可能不同。

### "2020_CBG_B01"

161 列；schema query ID：`01c7ba36-3204-bd57-0008-3d1a000175b6`；样例 query ID：`01c7ba36-3204-bb79-0008-3d1a0001576a`。

| 精确列名 | Snowflake 类型 | 字段含义（字典/名称） |
| --- | --- | --- |
| `"CENSUS_BLOCK_GROUP"` | VARCHAR(16777216) | CBG 地理标识；保持字符串及前导零。 |
| `"B01001e1"` | FLOAT | Sex By Age: Estimate / Total |
| `"B01001m1"` | FLOAT | Sex By Age: MarginOfError / Total |
| `"B01001e2"` | FLOAT | Sex By Age: Estimate / Total / Male |
| `"B01001m2"` | FLOAT | Sex By Age: MarginOfError / Total / Male |
| `"B01001e3"` | FLOAT | Sex By Age: Estimate / Total / Male / Under 5 years |
| `"B01001m3"` | FLOAT | Sex By Age: MarginOfError / Total / Male / Under 5 years |
| `"B01001e4"` | FLOAT | Sex By Age: Estimate / Total / Male / 5 to 9 years |
| `"B01001m4"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 5 to 9 years |
| `"B01001e5"` | FLOAT | Sex By Age: Estimate / Total / Male / 10 to 14 years |
| `"B01001m5"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 10 to 14 years |
| `"B01001e6"` | FLOAT | Sex By Age: Estimate / Total / Male / 15 to 17 years |
| `"B01001m6"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 15 to 17 years |
| `"B01001e7"` | FLOAT | Sex By Age: Estimate / Total / Male / 18 and 19 years |
| `"B01001m7"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 18 and 19 years |
| `"B01001e8"` | FLOAT | Sex By Age: Estimate / Total / Male / 20 years |
| `"B01001m8"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 20 years |
| `"B01001e9"` | FLOAT | Sex By Age: Estimate / Total / Male / 21 years |
| `"B01001m9"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 21 years |
| `"B01001e10"` | FLOAT | Sex By Age: Estimate / Total / Male / 22 to 24 years |
| `"B01001m10"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 22 to 24 years |
| `"B01001e11"` | FLOAT | Sex By Age: Estimate / Total / Male / 25 to 29 years |
| `"B01001m11"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 25 to 29 years |
| `"B01001e12"` | FLOAT | Sex By Age: Estimate / Total / Male / 30 to 34 years |
| `"B01001m12"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 30 to 34 years |
| `"B01001e13"` | FLOAT | Sex By Age: Estimate / Total / Male / 35 to 39 years |
| `"B01001m13"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 35 to 39 years |
| `"B01001e14"` | FLOAT | Sex By Age: Estimate / Total / Male / 40 to 44 years |
| `"B01001m14"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 40 to 44 years |
| `"B01001e15"` | FLOAT | Sex By Age: Estimate / Total / Male / 45 to 49 years |
| `"B01001m15"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 45 to 49 years |
| `"B01001e16"` | FLOAT | Sex By Age: Estimate / Total / Male / 50 to 54 years |
| `"B01001m16"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 50 to 54 years |
| `"B01001e17"` | FLOAT | Sex By Age: Estimate / Total / Male / 55 to 59 years |
| `"B01001m17"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 55 to 59 years |
| `"B01001e18"` | FLOAT | Sex By Age: Estimate / Total / Male / 60 and 61 years |
| `"B01001m18"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 60 and 61 years |
| `"B01001e19"` | FLOAT | Sex By Age: Estimate / Total / Male / 62 to 64 years |
| `"B01001m19"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 62 to 64 years |
| `"B01001e20"` | FLOAT | Sex By Age: Estimate / Total / Male / 65 and 66 years |
| `"B01001m20"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 65 and 66 years |
| `"B01001e21"` | FLOAT | Sex By Age: Estimate / Total / Male / 67 to 69 years |
| `"B01001m21"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 67 to 69 years |
| `"B01001e22"` | FLOAT | Sex By Age: Estimate / Total / Male / 70 to 74 years |
| `"B01001m22"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 70 to 74 years |
| `"B01001e23"` | FLOAT | Sex By Age: Estimate / Total / Male / 75 to 79 years |
| `"B01001m23"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 75 to 79 years |
| `"B01001e24"` | FLOAT | Sex By Age: Estimate / Total / Male / 80 to 84 years |
| `"B01001m24"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 80 to 84 years |
| `"B01001e25"` | FLOAT | Sex By Age: Estimate / Total / Male / 85 years and over |
| `"B01001m25"` | FLOAT | Sex By Age: MarginOfError / Total / Male / 85 years and over |
| `"B01001e26"` | FLOAT | Sex By Age: Estimate / Total / Female |
| `"B01001m26"` | FLOAT | Sex By Age: MarginOfError / Total / Female |
| `"B01001e27"` | FLOAT | Sex By Age: Estimate / Total / Female / Under 5 years |
| `"B01001m27"` | FLOAT | Sex By Age: MarginOfError / Total / Female / Under 5 years |
| `"B01001e28"` | FLOAT | Sex By Age: Estimate / Total / Female / 5 to 9 years |
| `"B01001m28"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 5 to 9 years |
| `"B01001e29"` | FLOAT | Sex By Age: Estimate / Total / Female / 10 to 14 years |
| `"B01001m29"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 10 to 14 years |
| `"B01001e30"` | FLOAT | Sex By Age: Estimate / Total / Female / 15 to 17 years |
| `"B01001m30"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 15 to 17 years |
| `"B01001e31"` | FLOAT | Sex By Age: Estimate / Total / Female / 18 and 19 years |
| `"B01001m31"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 18 and 19 years |
| `"B01001e32"` | FLOAT | Sex By Age: Estimate / Total / Female / 20 years |
| `"B01001m32"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 20 years |
| `"B01001e33"` | FLOAT | Sex By Age: Estimate / Total / Female / 21 years |
| `"B01001m33"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 21 years |
| `"B01001e34"` | FLOAT | Sex By Age: Estimate / Total / Female / 22 to 24 years |
| `"B01001m34"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 22 to 24 years |
| `"B01001e35"` | FLOAT | Sex By Age: Estimate / Total / Female / 25 to 29 years |
| `"B01001m35"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 25 to 29 years |
| `"B01001e36"` | FLOAT | Sex By Age: Estimate / Total / Female / 30 to 34 years |
| `"B01001m36"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 30 to 34 years |
| `"B01001e37"` | FLOAT | Sex By Age: Estimate / Total / Female / 35 to 39 years |
| `"B01001m37"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 35 to 39 years |
| `"B01001e38"` | FLOAT | Sex By Age: Estimate / Total / Female / 40 to 44 years |
| `"B01001m38"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 40 to 44 years |
| `"B01001e39"` | FLOAT | Sex By Age: Estimate / Total / Female / 45 to 49 years |
| `"B01001m39"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 45 to 49 years |
| `"B01001e40"` | FLOAT | Sex By Age: Estimate / Total / Female / 50 to 54 years |
| `"B01001m40"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 50 to 54 years |
| `"B01001e41"` | FLOAT | Sex By Age: Estimate / Total / Female / 55 to 59 years |
| `"B01001m41"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 55 to 59 years |
| `"B01001e42"` | FLOAT | Sex By Age: Estimate / Total / Female / 60 and 61 years |
| `"B01001m42"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 60 and 61 years |
| `"B01001e43"` | FLOAT | Sex By Age: Estimate / Total / Female / 62 to 64 years |
| `"B01001m43"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 62 to 64 years |
| `"B01001e44"` | FLOAT | Sex By Age: Estimate / Total / Female / 65 and 66 years |
| `"B01001m44"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 65 and 66 years |
| `"B01001e45"` | FLOAT | Sex By Age: Estimate / Total / Female / 67 to 69 years |
| `"B01001m45"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 67 to 69 years |
| `"B01001e46"` | FLOAT | Sex By Age: Estimate / Total / Female / 70 to 74 years |
| `"B01001m46"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 70 to 74 years |
| `"B01001e47"` | FLOAT | Sex By Age: Estimate / Total / Female / 75 to 79 years |
| `"B01001m47"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 75 to 79 years |
| `"B01001e48"` | FLOAT | Sex By Age: Estimate / Total / Female / 80 to 84 years |
| `"B01001m48"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 80 to 84 years |
| `"B01001e49"` | FLOAT | Sex By Age: Estimate / Total / Female / 85 years and over |
| `"B01001m49"` | FLOAT | Sex By Age: MarginOfError / Total / Female / 85 years and over |
| `"B01002e1"` | FLOAT | Median Age By Sex: Estimate / Median age / Total |
| `"B01002m1"` | FLOAT | Median Age By Sex: MarginOfError / Median age / Total |
| `"B01002e2"` | FLOAT | Median Age By Sex: Estimate / Median age / Male |
| `"B01002m2"` | FLOAT | Median Age By Sex: MarginOfError / Median age / Male |
| `"B01002e3"` | FLOAT | Median Age By Sex: Estimate / Median age / Female |
| `"B01002m3"` | FLOAT | Median Age By Sex: MarginOfError / Median age / Female |
| `"B01002Ae1"` | FLOAT | Median Age By Sex (White Alone): Estimate / Median age / Total |
| `"B01002Am1"` | FLOAT | Median Age By Sex (White Alone): MarginOfError / Median age / Total |
| `"B01002Ae2"` | FLOAT | Median Age By Sex (White Alone): Estimate / Median age / Male |
| `"B01002Am2"` | FLOAT | Median Age By Sex (White Alone): MarginOfError / Median age / Male |
| `"B01002Ae3"` | FLOAT | Median Age By Sex (White Alone): Estimate / Median age / Female |
| `"B01002Am3"` | FLOAT | Median Age By Sex (White Alone): MarginOfError / Median age / Female |
| `"B01002Be1"` | FLOAT | Median Age By Sex (Black Or African American Alone): Estimate / Median age / Total |
| `"B01002Bm1"` | FLOAT | Median Age By Sex (Black Or African American Alone): MarginOfError / Median age / Total |
| `"B01002Be2"` | FLOAT | Median Age By Sex (Black Or African American Alone): Estimate / Median age / Male |
| `"B01002Bm2"` | FLOAT | Median Age By Sex (Black Or African American Alone): MarginOfError / Median age / Male |
| `"B01002Be3"` | FLOAT | Median Age By Sex (Black Or African American Alone): Estimate / Median age / Female |
| `"B01002Bm3"` | FLOAT | Median Age By Sex (Black Or African American Alone): MarginOfError / Median age / Female |
| `"B01002Ce1"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): Estimate / Median age / Total |
| `"B01002Cm1"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): MarginOfError / Median age / Total |
| `"B01002Ce2"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): Estimate / Median age / Male |
| `"B01002Cm2"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): MarginOfError / Median age / Male |
| `"B01002Ce3"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): Estimate / Median age / Female |
| `"B01002Cm3"` | FLOAT | Median Age By Sex (American Indian And Alaska Native Alone): MarginOfError / Median age / Female |
| `"B01002De1"` | FLOAT | Median Age By Sex (Asian Alone): Estimate / Median age / Total |
| `"B01002Dm1"` | FLOAT | Median Age By Sex (Asian Alone): MarginOfError / Median age / Total |
| `"B01002De2"` | FLOAT | Median Age By Sex (Asian Alone): Estimate / Median age / Male |
| `"B01002Dm2"` | FLOAT | Median Age By Sex (Asian Alone): MarginOfError / Median age / Male |
| `"B01002De3"` | FLOAT | Median Age By Sex (Asian Alone): Estimate / Median age / Female |
| `"B01002Dm3"` | FLOAT | Median Age By Sex (Asian Alone): MarginOfError / Median age / Female |
| `"B01002Ee1"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Em1"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Ee2"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Em2"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Ee3"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Em3"` | FLOAT | 具体语义待字典核实。 |
| `"B01002Fe1"` | FLOAT | Median Age By Sex (Some Other Race Alone): Estimate / Median age / Total |
| `"B01002Fm1"` | FLOAT | Median Age By Sex (Some Other Race Alone): MarginOfError / Median age / Total |
| `"B01002Fe2"` | FLOAT | Median Age By Sex (Some Other Race Alone): Estimate / Median age / Male |
| `"B01002Fm2"` | FLOAT | Median Age By Sex (Some Other Race Alone): MarginOfError / Median age / Male |
| `"B01002Fe3"` | FLOAT | Median Age By Sex (Some Other Race Alone): Estimate / Median age / Female |
| `"B01002Fm3"` | FLOAT | Median Age By Sex (Some Other Race Alone): MarginOfError / Median age / Female |
| `"B01002Ge1"` | FLOAT | Median Age By Sex (Two Or More Races): Estimate / Median age / Total |
| `"B01002Gm1"` | FLOAT | Median Age By Sex (Two Or More Races): MarginOfError / Median age / Total |
| `"B01002Ge2"` | FLOAT | Median Age By Sex (Two Or More Races): Estimate / Median age / Male |
| `"B01002Gm2"` | FLOAT | Median Age By Sex (Two Or More Races): MarginOfError / Median age / Male |
| `"B01002Ge3"` | FLOAT | Median Age By Sex (Two Or More Races): Estimate / Median age / Female |
| `"B01002Gm3"` | FLOAT | Median Age By Sex (Two Or More Races): MarginOfError / Median age / Female |
| `"B01002He1"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): Estimate / Median age / Total |
| `"B01002Hm1"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): MarginOfError / Median age / Total |
| `"B01002He2"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): Estimate / Median age / Male |
| `"B01002Hm2"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): MarginOfError / Median age / Male |
| `"B01002He3"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): Estimate / Median age / Female |
| `"B01002Hm3"` | FLOAT | Median Age By Sex (White Alone, Not Hispanic Or Latino): MarginOfError / Median age / Female |
| `"B01002Ie1"` | FLOAT | Median Age By Sex (Hispanic Or Latino): Estimate / Median age / Total |
| `"B01002Im1"` | FLOAT | Median Age By Sex (Hispanic Or Latino): MarginOfError / Median age / Total |
| `"B01002Ie2"` | FLOAT | Median Age By Sex (Hispanic Or Latino): Estimate / Median age / Male |
| `"B01002Im2"` | FLOAT | Median Age By Sex (Hispanic Or Latino): MarginOfError / Median age / Male |
| `"B01002Ie3"` | FLOAT | Median Age By Sex (Hispanic Or Latino): Estimate / Median age / Female |
| `"B01002Im3"` | FLOAT | Median Age By Sex (Hispanic Or Latino): MarginOfError / Median age / Female |
| `"B01003e1"` | FLOAT | Total Population: Estimate / Total |
| `"B01003m1"` | FLOAT | Total Population: MarginOfError / Total |

五行样例（重要字段）：

| CENSUS_BLOCK_GROUP | B01001e1 | B01001m1 | B01001e2 | B01001e26 | B01002e1 |
| --- | --- | --- | --- | --- | --- |
| 010010201001 | 674.0 | 192.0 | 284.0 | 390.0 | 46.2 |
| 010010201002 | 1267.0 | 401.0 | 694.0 | 573.0 | 36.0 |
| 010010202001 | 706.0 | 200.0 | 354.0 | 352.0 | 31.6 |
| 010010202002 | 1051.0 | 229.0 | 656.0 | 395.0 | 38.8 |
| 010010203001 | 2912.0 | 565.0 | 1461.0 | 1451.0 | 35.5 |

### "2020_REDISTRICTING_CBG_DATA"

299 列；schema query ID：`01c7ba36-3204-bd12-0008-3d1a000165b6`；样例 query ID：`01c7ba36-3204-bb79-0008-3d1a0001576e`。

| 精确列名 | Snowflake 类型 | 字段含义（字典/名称） |
| --- | --- | --- |
| `"CENSUS_BLOCK_GROUP"` | VARCHAR(16777216) | CBG 地理标识；保持字符串及前导零。 |
| `"P0010001"` | NUMBER(38,0) | RACE: Total; universe=Total population |
| `"P0010002"` | NUMBER(38,0) | RACE: Population of one race; universe=Total population |
| `"P0010003"` | NUMBER(38,0) | RACE: White alone; universe=Total population |
| `"P0010004"` | NUMBER(38,0) | RACE: Black or African American alone; universe=Total population |
| `"P0010005"` | NUMBER(38,0) | RACE: American Indian and Alaska Native alone; universe=Total population |
| `"P0010006"` | NUMBER(38,0) | RACE: Asian alone; universe=Total population |
| `"P0010007"` | NUMBER(38,0) | RACE: Native Hawaiian and Other Pacific Islander alone; universe=Total population |
| `"P0010008"` | NUMBER(38,0) | RACE: Some Other Race alone; universe=Total population |
| `"P0010009"` | NUMBER(38,0) | RACE: Population of two or more races; universe=Total population |
| `"P0010010"` | NUMBER(38,0) | RACE: Population of two races; universe=Total population |
| `"P0010011"` | NUMBER(38,0) | RACE: White; Black or African American; universe=Total population |
| `"P0010012"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; universe=Total population |
| `"P0010013"` | NUMBER(38,0) | RACE: White; Asian; universe=Total population |
| `"P0010014"` | NUMBER(38,0) | RACE: White; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010015"` | NUMBER(38,0) | RACE: White; Some Other Race; universe=Total population |
| `"P0010016"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; universe=Total population |
| `"P0010017"` | NUMBER(38,0) | RACE: Black or African American; Asian; universe=Total population |
| `"P0010018"` | NUMBER(38,0) | RACE: Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010019"` | NUMBER(38,0) | RACE: Black or African American; Some Other Race; universe=Total population |
| `"P0010020"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Asian; universe=Total population |
| `"P0010021"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010022"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0010023"` | NUMBER(38,0) | RACE: Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010024"` | NUMBER(38,0) | RACE: Asian; Some Other Race; universe=Total population |
| `"P0010025"` | NUMBER(38,0) | RACE: Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010026"` | NUMBER(38,0) | RACE: Population of three races; universe=Total population |
| `"P0010027"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; universe=Total population |
| `"P0010028"` | NUMBER(38,0) | RACE: White; Black or African American; Asian; universe=Total population |
| `"P0010029"` | NUMBER(38,0) | RACE: White; Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010030"` | NUMBER(38,0) | RACE: White; Black or African American; Some Other Race; universe=Total population |
| `"P0010031"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0010032"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010033"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0010034"` | NUMBER(38,0) | RACE: White; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010035"` | NUMBER(38,0) | RACE: White; Asian; Some Other Race; universe=Total population |
| `"P0010036"` | NUMBER(38,0) | RACE: White; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010037"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0010038"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010039"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0010040"` | NUMBER(38,0) | RACE: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010041"` | NUMBER(38,0) | RACE: Black or African American; Asian; Some Other Race; universe=Total population |
| `"P0010042"` | NUMBER(38,0) | RACE: Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010043"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010044"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0010045"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010046"` | NUMBER(38,0) | RACE: Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010047"` | NUMBER(38,0) | RACE: Population of four races; universe=Total population |
| `"P0010048"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0010049"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010050"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0010051"` | NUMBER(38,0) | RACE: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010052"` | NUMBER(38,0) | RACE: White; Black or African American; Asian; Some Other Race; universe=Total population |
| `"P0010053"` | NUMBER(38,0) | RACE: White; Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010054"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010055"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0010056"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010057"` | NUMBER(38,0) | RACE: White; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010058"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010059"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0010060"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010061"` | NUMBER(38,0) | RACE: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010062"` | NUMBER(38,0) | RACE: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010063"` | NUMBER(38,0) | RACE: Population of five races; universe=Total population |
| `"P0010064"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0010065"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0010066"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010067"` | NUMBER(38,0) | RACE: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010068"` | NUMBER(38,0) | RACE: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010069"` | NUMBER(38,0) | RACE: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0010070"` | NUMBER(38,0) | RACE: Population of six races; universe=Total population |
| `"P0010071"` | NUMBER(38,0) | RACE: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020001"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Total; universe=Total population |
| `"P0020002"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Hispanic or Latino; universe=Total population |
| `"P0020003"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Not Hispanic or Latino; universe=Total population |
| `"P0020004"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of one race; universe=Total population |
| `"P0020005"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White alone; universe=Total population |
| `"P0020006"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American alone; universe=Total population |
| `"P0020007"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native alone; universe=Total population |
| `"P0020008"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Asian alone; universe=Total population |
| `"P0020009"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Native Hawaiian and Other Pacific Islander alone; universe=Total population |
| `"P0020010"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Some Other Race alone; universe=Total population |
| `"P0020011"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of two or more races; universe=Total population |
| `"P0020012"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of two races; universe=Total population |
| `"P0020013"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; universe=Total population |
| `"P0020014"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; universe=Total population |
| `"P0020015"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Asian; universe=Total population |
| `"P0020016"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020017"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Some Other Race; universe=Total population |
| `"P0020018"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; universe=Total population |
| `"P0020019"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Asian; universe=Total population |
| `"P0020020"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020021"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Some Other Race; universe=Total population |
| `"P0020022"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Asian; universe=Total population |
| `"P0020023"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020024"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0020025"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020026"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Asian; Some Other Race; universe=Total population |
| `"P0020027"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020028"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of three races; universe=Total population |
| `"P0020029"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; universe=Total population |
| `"P0020030"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Asian; universe=Total population |
| `"P0020031"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020032"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Some Other Race; universe=Total population |
| `"P0020033"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0020034"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020035"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0020036"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020037"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Asian; Some Other Race; universe=Total population |
| `"P0020038"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020039"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0020040"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020041"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0020042"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020043"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Asian; Some Other Race; universe=Total population |
| `"P0020044"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020045"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020046"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0020047"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020048"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020049"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of four races; universe=Total population |
| `"P0020050"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Asian; universe=Total population |
| `"P0020051"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020052"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population |
| `"P0020053"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020054"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Asian; Some Other Race; universe=Total population |
| `"P0020055"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020056"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020057"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0020058"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020059"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020060"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020061"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0020062"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020063"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020064"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020065"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of five races; universe=Total population |
| `"P0020066"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population |
| `"P0020067"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population |
| `"P0020068"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020069"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020070"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020071"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0020072"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: Population of six races; universe=Total population |
| `"P0020073"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population |
| `"P0030001"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Total; universe=Total population 18 years and over |
| `"P0030002"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of one race; universe=Total population 18 years and over |
| `"P0030003"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White alone; universe=Total population 18 years and over |
| `"P0030004"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American alone; universe=Total population 18 years and over |
| `"P0030005"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native alone; universe=Total population 18 years and over |
| `"P0030006"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Asian alone; universe=Total population 18 years and over |
| `"P0030007"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Native Hawaiian and Other Pacific Islander alone; universe=Total population 18 years and over |
| `"P0030008"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Some Other Race alone; universe=Total population 18 years and over |
| `"P0030009"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of two or more races; universe=Total population 18 years and over |
| `"P0030010"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of two races; universe=Total population 18 years and over |
| `"P0030011"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; universe=Total population 18 years and over |
| `"P0030012"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0030013"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; universe=Total population 18 years and over |
| `"P0030014"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030015"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Some Other Race; universe=Total population 18 years and over |
| `"P0030016"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0030017"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; universe=Total population 18 years and over |
| `"P0030018"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030019"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Some Other Race; universe=Total population 18 years and over |
| `"P0030020"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0030021"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030022"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0030023"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030024"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030025"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030026"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of three races; universe=Total population 18 years and over |
| `"P0030027"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0030028"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; universe=Total population 18 years and over |
| `"P0030029"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030030"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Some Other Race; universe=Total population 18 years and over |
| `"P0030031"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0030032"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030033"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0030034"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030035"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030036"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030037"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0030038"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030039"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0030040"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030041"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030042"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030043"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030044"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030045"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030046"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030047"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of four races; universe=Total population 18 years and over |
| `"P0030048"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0030049"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030050"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0030051"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030052"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030053"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030054"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030055"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030056"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030057"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030058"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030059"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030060"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030061"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030062"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030063"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of five races; universe=Total population 18 years and over |
| `"P0030064"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0030065"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0030066"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030067"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030068"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030069"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0030070"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: Population of six races; universe=Total population 18 years and over |
| `"P0030071"` | NUMBER(38,0) | RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040001"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Total; universe=Total population 18 years and over |
| `"P0040002"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Hispanic or Latino; universe=Total population 18 years and over |
| `"P0040003"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Not Hispanic or Latino; universe=Total population 18 years and over |
| `"P0040004"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of one race; universe=Total population 18 years and over |
| `"P0040005"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White alone; universe=Total population 18 years and over |
| `"P0040006"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American alone; universe=Total population 18 years and over |
| `"P0040007"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native alone; universe=Total population 18 years and over |
| `"P0040008"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Asian alone; universe=Total population 18 years and over |
| `"P0040009"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Native Hawaiian and Other Pacific Islander alone; universe=Total population 18 years and over |
| `"P0040010"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Some Other Race alone; universe=Total population 18 years and over |
| `"P0040011"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of two or more races; universe=Total population 18 years and over |
| `"P0040012"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of two races; universe=Total population 18 years and over |
| `"P0040013"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; universe=Total population 18 years and over |
| `"P0040014"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0040015"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; universe=Total population 18 years and over |
| `"P0040016"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040017"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Some Other Race; universe=Total population 18 years and over |
| `"P0040018"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0040019"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; universe=Total population 18 years and over |
| `"P0040020"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040021"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Some Other Race; universe=Total population 18 years and over |
| `"P0040022"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0040023"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040024"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0040025"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040026"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040027"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040028"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of three races; universe=Total population 18 years and over |
| `"P0040029"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; universe=Total population 18 years and over |
| `"P0040030"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; universe=Total population 18 years and over |
| `"P0040031"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040032"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Some Other Race; universe=Total population 18 years and over |
| `"P0040033"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0040034"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040035"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0040036"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040037"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040038"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040039"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0040040"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040041"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0040042"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040043"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040044"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040045"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040046"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040047"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040048"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040049"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of four races; universe=Total population 18 years and over |
| `"P0040050"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; universe=Total population 18 years and over |
| `"P0040051"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040052"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Some Other Race; universe=Total population 18 years and over |
| `"P0040053"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040054"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040055"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040056"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040057"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040058"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040059"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040060"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040061"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040062"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040063"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040064"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040065"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of five races; universe=Total population 18 years and over |
| `"P0040066"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; universe=Total population 18 years and over |
| `"P0040067"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Some Other Race; universe=Total population 18 years and over |
| `"P0040068"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040069"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040070"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040071"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0040072"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: Population of six races; universe=Total population 18 years and over |
| `"P0040073"` | NUMBER(38,0) | HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER: White; Black or African American; American Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; Some Other Race; universe=Total population 18 years and over |
| `"P0050001"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Total; universe=Population in group quarters |
| `"P0050002"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Institutionalized population; universe=Population in group quarters |
| `"P0050003"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Correctional facilities for adults; universe=Population in group quarters |
| `"P0050004"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Juvenile facilities; universe=Population in group quarters |
| `"P0050005"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Nursing facilities/Skilled-nursing facilities; universe=Population in group quarters |
| `"P0050006"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Other institutional facilities; universe=Population in group quarters |
| `"P0050007"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Noninstitutionalized population; universe=Population in group quarters |
| `"P0050008"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: College/University student housing; universe=Population in group quarters |
| `"P0050009"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Military quarters; universe=Population in group quarters |
| `"P0050010"` | NUMBER(38,0) | GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE: Other noninstitutional facilities; universe=Population in group quarters |

五行样例（重要字段）：

| CENSUS_BLOCK_GROUP | P0010001 | P0010003 | P0010004 |
| --- | --- | --- | --- |
| 010010201001 | 575 | 433 | 73 |
| 010010201002 | 1200 | 956 | 140 |
| 010010202001 | 974 | 311 | 615 |
| 010010202002 | 1081 | 531 | 489 |
| 010010203001 | 2377 | 1672 | 499 |

### "2020_METADATA_CBG_GEOGRAPHIC_DATA"

5 列；schema query ID：`01c7ba36-3204-bd12-0008-3d1a000165ba`；样例 query ID：`01c7ba36-3204-bd57-0008-3d1a000175ba`。

| 精确列名 | Snowflake 类型 | 字段含义（字典/名称） |
| --- | --- | --- |
| `"CENSUS_BLOCK_GROUP"` | VARCHAR(16777216) | CBG 地理标识；保持字符串及前导零。 |
| `"AMOUNT_LAND"` | NUMBER(38,0) | 土地面积；单位未确认。 |
| `"AMOUNT_WATER"` | NUMBER(38,0) | 水域面积；单位未确认。 |
| `"LATITUDE"` | FLOAT | 纬度。 |
| `"LONGITUDE"` | FLOAT | 经度。 |

五行样例（重要字段）：

| CENSUS_BLOCK_GROUP | AMOUNT_LAND | AMOUNT_WATER | LATITUDE | LONGITUDE |
| --- | --- | --- | --- | --- |
| 010010201001 | 4264299 | 28435 | 32.465832 | -86.4896607 |
| 010010201002 | 5561005 | 0 | 32.4858732 | -86.4896724 |
| 010010202001 | 2058374 | 0 | 32.4800823 | -86.4749744 |
| 010010202002 | 1262444 | 5669 | 32.464435 | -86.4697659 |
| 010010203001 | 3866513 | 9054 | 32.480175 | -86.4607925 |

## 字典与地理关联

- `2020_METADATA_CBG_FIELD_DESCRIPTIONS`：`TABLE_ID` 是数据列名，例如 `B01001e1`；`TABLE_NUMBER` 是原始表号；还有 `TABLE_TITLE`、`TABLE_TOPICS`、`TABLE_UNIVERSE` 与分层说明。
- 该字典中真实存在拼写为 `FIELD_LEVELl_9` 的列（LEVEL 后有小写 l）；不要改写为不存在的 `FIELD_LEVEL_9`。
- `2020_REDISTRICTING_METADATA_CBG_FIELD_DESCRIPTIONS`：`COLUMN_ID` 对应人口表列名，`FIELD_NAME`、`COLUMN_TOPIC`、`COLUMN_UNIVERSE` 给出含义。
- `2020_METADATA_CBG_FIPS_CODES` 实测列：`STATE`、`STATE_FIPS`、`COUNTY_FIPS`、`COUNTY`、`CLASS_CODE`；五行样例与列类型见元数据证据。
- 关联 CBG 表时用精确的 `"CENSUS_BLOCK_GROUP"`。样例编码为 12 位字符串；州/县编码可分别从前 2 位和第 3–5 位提取，与 FIPS 字符串比较，保留前导零。关联键唯一性与覆盖率尚未评估。

## 已发现的注意点与限制

1. 标识符：表名以数字开头，人口列名混合大小写（如 `B01001e1`）；统一双引号并将内部双引号转义。参数绑定用于模型/提示值，不可代替任意标识符拼接。
2. 估计与误差：`B01001e1` 是总人口 Estimate，`B01001m1` 是 MarginOfError；不能把误差列当人口或把不同细分类重复相加。
3. 数据来源不同：相同 CBG `010010201001` 的 B01 总人口样例为 674，重划选区 `P0010001` 为 575。它们是不同统计产品，不应混用为同一人口口径。
4. 年份与覆盖：2019 B/C 表为 220333 行，2020 B/C 表为 242335 行；地理表和 patterns 的行数还可能不同。年份边界、覆盖范围、重复/缺失键需在 agent 评价阶段另查。
5. 本次仅确认表读取、schema 和模型连通性，未验证完整 agent、任意 SQL 生成安全性、答案 grounding、全国人口口径、并发、吞吐量或成本。
6. 对 metadata 字典执行全量读取后，仅保留核心表相关字段以控制证据体积；JSON 的 observed_row_count、retained_row_count 和 retention_note 明确标记该处理。

## 仓库节省 credit 与最终状态

- 实测仓库：X-Small，AUTO_SUSPEND=60 秒，AUTO_RESUME=true。未修改仓库规模、自动暂停配置或区域。
- 完整 probe 的 ALTER SUSPEND 成功，query ID：`01c7ba36-3204-bb79-0008-3d1a00015776`；SHOW 确认 `SUSPENDED`。
- 最后的字段字典查询结束后再次暂停，query ID：`01c7ba37-3204-bb79-0008-3d1a0001578e`；SHOW 确认 `SUSPENDED`，query ID：`01c7ba37-3204-bd57-0008-3d1a000175d2`。
- inventory 阶段仓库原本已暂停，ALTER 返回 invalid state；脚本通过 SHOW 确认已暂停，没有将错误误报为 ALTER 成功。
- 未来若需要手动暂停，USAGE 不等同于 OPERATE；本次 ALTER 已实测成功。
  参见 [ALTER WAREHOUSE 权限文档](https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse)。
- 暂停仓库不能代替停止 Cortex 调用；不要持续运行未授权的模型测试。本次没有留下后台循环或服务。

## 证据文件与本地检查

- `docs/snowflake_inventory.json`：首次真实上下文、表清单和暂停检查。
- `docs/snowflake_evidence.json`：71 表 + 2 视图的 COUNT(*)、三个核心 schema/五行完整样例、四个模型结果和最终暂停状态。
- `docs/snowflake_metadata.json`：字段字典、FIPS 样例、核心字段含义和最后一次暂停状态。
- `tests/test_snowflake_probe.py`：仅为本地确定性单元测试，连接/cursor doubles 明确属于 mocks；不替代上述真实远程结果。

本轮执行结果：

| 检查 | 实际结果 |
| --- | --- |
| `bash scripts/doctor.sh` | exit 0；仅检查进程环境，不加载 .env，因此 MISSING in process environment 不代表连接配置缺失。真实 probe 已通过 .env 连接成功。 |
| `bash scripts/verify.sh` | exit 0；Ruff format/check 通过；14 个确定性单元测试通过。 |
| `bash scripts/preflight.sh` | exit 2；完整挑战模板仍 pending、本轮文件未提交；无已发现的凭据文件名风险。 |
| `.venv/bin/python -m pip check` | exit 0；无损坏依赖。 |
| `git diff --check` | exit 0；无空白错误。 |

ShellCheck 未安装，明确标记 SKIP，未宣称其通过。以上单元测试是 mocks；
Snowflake 数据/Cortex 通路验证来自保存的实际远程结果。环境层已就绪，
完整聊天 agent 和最终交付质量门仍待后续实现与评估。
