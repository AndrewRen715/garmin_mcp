***

name: "garmin-running"
description: "Analyzes recent running activities with per-kilometer splits, uses personal heart rate zones, and generates training status reports. Invoke when user asks to analyze running data, check training status, or get performance trends."
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Garmin Running Analysis Skill

This skill helps analyze Garmin running activities and provides training insights.

## What It Does

- Analyzes recent running activities with per-kilometer splits from Garmin Connect
- Uses personal heart rate zones from me.md for accurate intensity analysis
- Generates comprehensive training status reports and performance trends
- Provides personalized training recommendations based on analysis
- Offers detailed performance insights and improvement suggestions

## When to Invoke

Invoke this skill when:

- User asks to analyze recent running activities
- User wants to check training status or progress
- User requests insights about running performance
- User needs recommendations for training improvement

## Usage Examples

### Example 1: Analyze Recent Run

**User Query:** "分析我最近的跑步活动"

**Skill Action:**

- Run `.\Scripts\analyze_recent_run_with_splits.py` to get latest activity data, per-kilometer splits, and heart rate analysis
- Read `.\References\Myrunningdata.md` to get personal heart rate zones and performance benchmarks
- Combine data to provide comprehensive analysis
- Generate training status report and performance trends

### Example 2: Check Training Status

**User Query:** "我的训练状态如何？"

**Skill Action:**

- Run `get_training_status.py` to fetch current training status
- Analyze recent training load and recovery
- Provide status summary and recommendations

### Example 3: Generate Performance Report

**User Query:** "生成我的跑步表现报告"

**Skill Action:**

- Collect recent running activities data
- Analyze performance trends and patterns
- Generate comprehensive report with insights

## Implementation Details

This skill leverages the following scripts and files:

- `analyze_recent_run_with_splits.py` - Gets latest activity data, per-kilometer splits, and heart rate analysis
- `get_training_status.py` - Fetches current training status data
- `analyze_training_data.py` - Analyzes training trends and patterns
- `me.md` - Contains personal heart rate zones and performance benchmarks

## Output Format

When invoking this skill, provide output in the following format:

1. **Activity Summary:** Key metrics of the analyzed run including per-kilometer splits
2. **Performance Analysis:** Detailed analysis based on personal heart rate zones from me.md
3. **Training Status Report:** Current training status and load
4. **Performance Trends:** Analysis of recent performance patterns
5. **Training Recommendations:** Personalized suggestions based on analysis
6. **Next Steps:** Potential follow-up actions

## Language Support

This skill supports both English and Chinese inputs/outputs based on user preference.
