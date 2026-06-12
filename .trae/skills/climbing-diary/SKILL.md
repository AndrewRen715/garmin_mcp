---
name: "climbing-diary"
description: "Updates climbing training diary. Automatically fetches recent climbing activities from Garmin Connect, updates 攀岩训练日记.md with proper format, and asks user to supplement missing information (location, route details, training feelings, etc.). Invoke when user says '更新攀岩日记', '记录攀岩训练' or '添加攀岩记录'."
---

# Climbing Diary Skill

This skill helps users automatically record and update their climbing training diary.

## Features

- Automatically fetches recent climbing activity records from Garmin Connect
- Updates `攀岩训练日记.md` in standard format
- Auto-fills Garmin data (duration, heart rate, calories, etc.)
- Intelligently identifies missing information and asks user to supplement
- Tracks milestone progress and training statistics

## When to Invoke

Invoke this skill when:
- User says "更新攀岩日记" (Update climbing diary)
- User says "记录攀岩训练" (Record climbing training)
- User says "添加攀岩记录" (Add climbing record)
- User requests to sync latest climbing activities to diary

## Usage Flow

### Step 1: Fetch Garmin Data

Run `Scripts/get_climbing_activities.py` to get recent climbing activities:

```python
# Key output fields
- Activity date and time
- Activity type (bouldering/lead climbing/mixed)
- Training duration
- Average HR / Max HR
- Calorie consumption
- Activity location (if available)
```

### Step 2: Update Diary File

Update `攀岩训练日记.md` with the following format:

```
### YYYY-MM-DD (Day X) - Location

**🎯 Training Type**: Lead Climbing / Bouldering / Mixed Training\
**📊 Garmin**: X minutes | Average XX BPM | Max XXX BPM

#### ✅ Completed Routes

| Difficulty | Color | Status | Notes |
| --- | --- | --- | --- |
| 5.9 | Orange | ✅ Completed | Warm-up route |

#### ⚠️ Challenges

| Difficulty | Color | Attempts | Stuck Point | Analysis |
| ----- | ---- | ---- | --------- | ----------- |
| 5.10a | Orange | 2 times | Middle/Last 5 points | Wrong route choice, hand exhaustion |

#### 💡 Summary

- **Training Duration**: XX minutes
- **Technical Progress**: Pace control and footwork awareness improved significantly
- **Areas to Improve**: Flag technique, route reading
- **Overall Feeling**: Good condition
```

### Step 3: Ask for Missing Information

Use `AskUserQuestion` tool to automatically detect and collect missing information from user:

1. **Location** - Climbing gym name (multiple choice options)
2. **Completed Routes** - Specific route difficulties (multi-select options: 5.9, 5.10a, 5.10b, etc.)
3. **Challenge/Breakthrough** - Training status (multiple choice: 有突破, 有挑战, 保持状态, 恢复训练)

**Tool Usage Example:**
```json
{
  "tool": "AskUserQuestion",
  "questions": [
    {
      "question": "请问这次训练是在哪个攀岩馆进行的？",
      "header": "攀岩馆",
      "options": [
        {"label": "大悦城 Luna", "description": "杭州大悦城 Luna 攀岩馆"},
        {"label": "顽攀西湖", "description": "顽攀西湖攀岩馆"},
        {"label": "Luna 城西", "description": "Luna 城西抱石馆"},
        {"label": "Golink 抱石馆", "description": "Golink 抱石馆"}
      ],
      "multiSelect": false
    },
    {
      "question": "这次训练完成了哪些难度的线路？",
      "header": "完成线路",
      "options": [
        {"label": "5.9", "description": "5.9 难度线路"},
        {"label": "5.10a", "description": "5.10a 难度线路"},
        {"label": "5.10b", "description": "5.10b 难度线路"},
        {"label": "其他", "description": "其他难度"}
      ],
      "multiSelect": true
    },
    {
      "question": "这次训练是否有特别的挑战或突破？",
      "header": "挑战/突破",
      "options": [
        {"label": "有突破", "description": "完成了新难度或攻克了难点"},
        {"label": "有挑战", "description": "尝试了有难度的线路但未完成"},
        {"label": "保持状态", "description": "维持训练状态"},
        {"label": "恢复训练", "description": "恢复性训练"}
      ],
      "multiSelect": false
    }
  ],
  "answers": [
    {"selected_options": ["大悦城 Luna"]},
    {"selected_options": ["5.9", "5.10a"]},
    {"selected_options": ["保持状态"]}
  ]
}
```

**User Input Handling:** After receiving user answers, parse the additional information field for detailed route notes and update the diary with specific color, difficulty, and progress details.

## Data Format Standards

### Activity Type Mapping

| Garmin Activity Type | Diary Type |
| ------------------- | ---------- |
| `indoor_climbing` | Lead Climbing |
| `rock_climbing` | Lead Climbing |
| `bouldering` | Bouldering |
| Mixed Training | Bouldering + Lead |

### Difficulty Identifiers

- **Lead Climbing**: 5.8, 5.9, 5.10a, 5.10b, 5.10c, 5.10d, 5.11...
- **Bouldering**: V0, V1, V2, V3, V4, V5...

## Output Format

After updating the diary, provide the following summary:

1. **Activity Overview**: Date, duration, heart rate, type
2. **Updated Content**: Location of new training record
3. **Missing Information**: Content that needs user supplement
4. **Milestone Update**: Whether new achievements were reached
5. **Training Statistics**: Total training sessions, cumulative duration, etc.

## Implementation Details

This skill leverages the following scripts and files:

- `Scripts/get_climbing_activities.py` - Fetches Garmin climbing activities
- `References/climbing_levels.md` - Current level and goals (optional)
- `攀岩训练日记.md` - Main diary file

## Notes

- Prioritize using existing `get_recent_climbing_activities.py` script
- Auto-filter non-climbing related activities
- For multiple same-day activities, merge records
- Maintain existing diary format consistency
- Regularly update milestone progress
