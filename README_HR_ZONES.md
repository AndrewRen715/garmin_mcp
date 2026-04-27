# 获取Garmin Connect中设置的心率区间

## 功能说明

garmin_mcp库支持获取用户在Garmin Connect中设置的心率区间。这些区间是用户在Garmin Connect网站或应用程序中配置的个性化心率训练区间。

## 使用方法

### 方法一：通过MCP服务器的工具获取

1. **启动MCP服务器**

   ```bash
   garmin-mcp
   ```

2. **使用`get_activity_hr_in_timezones`工具**

   该工具需要一个活动ID作为参数，它会返回该活动的心率区间数据，其中包含用户在Garmin Connect中设置的心率区间。

   **工具调用示例**：
   ```
   get_activity_hr_in_timezones(activity_id=1234567890)
   ```

3. **分析返回的数据**

   工具返回的数据中包含用户的心率区间设置，通常在`zones`或`heartRateZones`字段中。

### 方法二：使用提供的脚本

1. **运行`get_user_hr_zones.py`脚本**

   该脚本演示了如何通过MCP服务器获取用户的心率区间设置。

   ```bash
   python get_user_hr_zones.py
   ```

## 工作原理

1. **获取最近的活动**：脚本首先获取用户最近的活动列表。

2. **找到包含心率数据的活动**：从活动列表中找到第一个包含心率数据的活动。

3. **获取活动的心率区间数据**：使用`get_activity_hr_in_timezones`工具获取该活动的心率区间数据。

4. **分析数据**：从返回的数据中提取用户的心率区间设置。

## 数据结构

从Garmin Connect返回的心率区间数据通常具有以下结构：

```json
{
  "zones": [
    {"min": 0, "max": 100},
    {"min": 100, "max": 120},
    {"min": 120, "max": 140},
    {"min": 140, "max": 160},
    {"min": 160, "max": 220}
  ]
}
```

或者：

```json
{
  "heartRateZones": [
    {"min": 0, "max": 100},
    {"min": 100, "max": 120},
    {"min": 120, "max": 140},
    {"min": 140, "max": 160},
    {"min": 160, "max": 220}
  ]
}
```

## 注意事项

1. **需要有效的Garmin Connect账户**：使用前需要通过`garmin-mcp-auth`命令验证您的Garmin Connect账户。

2. **需要有包含心率数据的活动**：工具需要从活动数据中提取心率区间信息，因此需要至少有一个包含心率数据的活动。

3. **数据准确性**：返回的心率区间数据直接来自Garmin Connect，与用户在Garmin Connect中设置的区间完全一致。

## 示例输出

使用`get_activity_hr_in_timezones`工具获取心率区间数据的示例输出：

```json
{
  "zones": [
    {
      "min": 0,
      "max": 100
    },
    {
      "min": 100,
      "max": 120
    },
    {
      "min": 120,
      "max": 140
    },
    {
      "min": 140,
      "max": 160
    },
    {
      "min": 160,
      "max": 220
    }
  ],
  "timeInZones": [
    {
      "zone": 1,
      "seconds": 300
    },
    {
      "zone": 2,
      "seconds": 600
    },
    {
      "zone": 3,
      "seconds": 900
    },
    {
      "zone": 4,
      "seconds": 300
    },
    {
      "zone": 5,
      "seconds": 60
    }
  ]
}
```

## 故障排除

1. **工具调用失败**：确保活动ID正确，并且该活动包含心率数据。

2. **返回的数据中没有心率区间**：确保您在Garmin Connect中已经设置了心率区间。

3. **认证错误**：确保您的Garmin Connect账户已经通过`garmin-mcp-auth`命令验证。

## 相关文件

- `get_user_hr_zones.py`：演示如何获取用户的心率区间设置
- `test_hr_zones_direct.py`：直接使用garminconnect库测试心率区间功能
- `test_hr_zones.py`：通过garmin_mcp库测试心率区间功能
