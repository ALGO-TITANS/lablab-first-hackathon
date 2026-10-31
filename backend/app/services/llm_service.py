import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_code(
        self,
        query: str,
        schema_context: str,
        sample_rows: list[dict],
        force_error: bool = False
    ) -> Dict[str, Any]:
        """Generates analysis plan, Python code, and chart recommendation."""
        pass

    @abstractmethod
    async def diagnose_and_repair(
        self,
        query: str,
        schema_context: str,
        failed_code: str,
        error_type: str,
        error_message: str,
        traceback_str: str
    ) -> Dict[str, Any]:
        """Diagnoses failure and generates repaired Python code."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, high-quality AI provider for offline development,
    automated testing, and guaranteed hackathon demos without paid API quotas.
    """

    async def generate_code(
        self,
        query: str,
        schema_context: str,
        sample_rows: list[dict],
        force_error: bool = False
    ) -> Dict[str, Any]:
        q_lower = query.lower()

        # If force_error is requested (for demoing self-healing recovery)
        if force_error:
            return {
                "explanation": "Attempting initial data aggregation. (Note: Intentional column casing mismatch introduced for self-healing demonstration).",
                "code": (
                    "# Initial attempt with intentional typo in column name for demo\n"
                    "grouped = df.groupby('Region')['Revenue'].sum().reset_index()\n"
                    "result = {'data': grouped, 'chart_type': 'bar', 'summary': 'Aggregated revenue by region.'}"
                ),
                "chart_type": "bar"
            }

        # Intent: Missing values
        if "missing" in q_lower or "null" in q_lower:
            code = (
                "missing_summary = df.isna().sum().reset_index()\n"
                "missing_summary.columns = ['column_name', 'missing_count']\n"
                "missing_summary['missing_percentage'] = (missing_summary['missing_count'] / len(df) * 100).round(2)\n"
                "result = {\n"
                "    'data': missing_summary.to_dict(orient='records'),\n"
                "    'chart_type': 'bar',\n"
                "    'summary': f'Missing value analysis across {len(df.columns)} columns.'\n"
                "}"
            )
            return {
                "explanation": "Calculated total and percentage missing values across all columns in the dataset.",
                "code": code,
                "chart_type": "bar"
            }

        # Intent: Top products / categories / churn / grouping
        if "top" in q_lower or "highest" in q_lower or "best" in q_lower:
            # Check for revenue/sales in schema
            if "revenue" in schema_context.lower() or "sales" in schema_context.lower():
                metric = "revenue" if "revenue" in schema_context.lower() else "sales"
                group_col = "product_name" if "product" in q_lower else ("category" if "category" in q_lower else "region")
                code = (
                    f"top_items = df.groupby('{group_col}')['{metric}'].sum().reset_index()\n"
                    f"top_items = top_items.sort_values(by='{metric}', ascending=False).head(5)\n"
                    f"result = {{\n"
                    f"    'data': top_items.to_dict(orient='records'),\n"
                    f"    'chart_type': 'bar',\n"
                    f"    'summary': f'Top 5 {group_col}s ranked by total {metric}.'\n"
                    f"}}"
                )
                return {
                    "explanation": f"Identified top performing {group_col}s sorted by aggregate {metric}.",
                    "code": code,
                    "chart_type": "bar"
                }

        # Intent: Trend / Monthly / Time series
        if "trend" in q_lower or "month" in q_lower or "time" in q_lower or "date" in q_lower:
            code = (
                "# Parse dates and aggregate revenue over time\n"
                "df['date_parsed'] = pd.to_datetime(df['date'] if 'date' in df.columns else df.columns[1], errors='coerce')\n"
                "df['period'] = df['date_parsed'].dt.to_period('M').astype(str)\n"
                "metric_col = 'revenue' if 'revenue' in df.columns else df.select_dtypes(include='number').columns[0]\n"
                "trend = df.groupby('period')[metric_col].sum().reset_index()\n"
                "result = {\n"
                "    'data': trend.to_dict(orient='records'),\n"
                "    'chart_type': 'line',\n"
                "    'summary': f'Monthly trend for {metric_col}.'\n"
                "}"
            )
            return {
                "explanation": "Parsed date dimension and computed chronological trend metrics.",
                "code": code,
                "chart_type": "line"
            }

        # Intent: Region / Category comparison
        if "region" in q_lower or "category" in q_lower or "compare" in q_lower:
            group_col = "region" if "region" in q_lower else "category"
            code = (
                f"comparison = df.groupby('{group_col}').agg({{\n"
                f"    'revenue': 'sum',\n"
                f"    'profit': 'sum'\n"
                f"}}).reset_index() if 'profit' in df.columns and 'revenue' in df.columns else df.groupby('{group_col}').size().reset_index(name='count')\n"
                f"result = {{\n"
                f"    'data': comparison.to_dict(orient='records'),\n"
                f"    'chart_type': 'bar',\n"
                f"    'summary': f'Comparative breakdown by {group_col}.'\n"
                f"}}"
            )
            return {
                "explanation": f"Grouped data by {group_col} to analyze performance differences.",
                "code": code,
                "chart_type": "bar"
            }

        # Intent: Churn / Status / Distribution
        if "churn" in q_lower or "contract" in q_lower or "distribution" in q_lower or "pie" in q_lower:
            target_col = "churn_status" if "churn_status" in df_cols(schema_context) else ("contract_type" if "contract_type" in df_cols(schema_context) else "category")
            code = (
                f"dist = df['{target_col}'].value_counts().reset_index()\n"
                f"dist.columns = ['{target_col}', 'count']\n"
                f"result = {{\n"
                f"    'data': dist.to_dict(orient='records'),\n"
                f"    'chart_type': 'pie',\n"
                f"    'summary': f'Distribution of {target_col}.'\n"
                f"}}"
            )
            return {
                "explanation": f"Calculated categorical frequency breakdown for {target_col}.",
                "code": code,
                "chart_type": "pie"
            }

        # General numerical summary / average / stats
        code = (
            "num_df = df.select_dtypes(include='number')\n"
            "summary = num_df.describe().T.reset_index()\n"
            "summary.columns = ['metric', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']\n"
            "result = {\n"
            "    'data': summary.round(2).to_dict(orient='records'),\n"
            "    'chart_type': 'bar',\n"
            "    'summary': f'Descriptive summary statistics computed for {len(num_df.columns)} numeric variables.'\n"
            "}"
        )
        return {
            "explanation": "Computed statistical metrics and aggregations from the dataset.",
            "code": code,
            "chart_type": "bar"
        }

    async def diagnose_and_repair(
        self,
        query: str,
        schema_context: str,
        failed_code: str,
        error_type: str,
        error_message: str,
        traceback_str: str
    ) -> Dict[str, Any]:
        """
        Diagnoses error and returns repaired Pandas code.
        """
        diagnosis = (
            f"Detected {error_type}: '{error_message}'. "
            f"The failed code referenced a non-existent or mis-cased column name. "
            f"Inspected dataset schema to identify matching case-sensitive column attributes."
        )

        # Smart repair for KeyError / column casing / type mismatch
        repaired_code = (
            "# Repaired Pandas code with normalized column names\n"
            "col_map = {c.lower(): c for c in df.columns}\n"
            "# Pick distinct categorical column for grouping and numeric for aggregation\n"
            "cat_cols = df.select_dtypes(exclude='number').columns.tolist()\n"
            "group_col = cat_cols[0] if cat_cols else df.columns[0]\n"
            "for candidate in ['region', 'category', 'warehouse', 'product_name', 'customer_segment', 'contract_type']:\n"
            "    if candidate in col_map:\n"
            "        group_col = col_map[candidate]\n"
            "        break\n"
            "\n"
            "num_cols = [c for c in df.select_dtypes(include='number').columns.tolist() if c != group_col]\n"
            "val_col = num_cols[0] if num_cols else df.columns[-1]\n"
            "for candidate in ['revenue', 'stock', 'price', 'profit', 'units_sold', 'monthly_charges']:\n"
            "    if candidate in col_map and col_map[candidate] != group_col:\n"
            "        val_col = col_map[candidate]\n"
            "        break\n"
            "\n"
            "repaired_df = df.groupby(group_col, as_index=False)[val_col].sum()\n"
            "repaired_df.columns = ['category', 'total_value']\n"
            "result = {\n"
            "    'data': repaired_df.to_dict(orient='records'),\n"
            "    'chart_type': 'bar',\n"
            "    'summary': f'Successfully repaired execution. Aggregated {val_col} by {group_col}.'\n"
            "}"
        )

        return {
            "diagnosis": diagnosis,
            "repaired_code": repaired_code,
            "explanation": "Self-healing agent normalized column lookups using schema inspection and successfully recovered execution.",
            "chart_type": "bar"
        }


def df_cols(schema_context: str) -> list[str]:
    # Helper to extract column names mentioned in schema context
    try:
        return [c.strip() for c in re.findall(r"-\s*([a-zA-Z0-9_]+)", schema_context)]
    except Exception:
        return []


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_code(
        self,
        query: str,
        schema_context: str,
        sample_rows: list[dict],
        force_error: bool = False
    ) -> Dict[str, Any]:
        from google import genai
        client = genai.Client(api_key=self.api_key)

        prompt = f"""
You are an expert Data Scientist and Python/Pandas developer.
Given the dataset schema and sample rows below, write executable Python code to answer the user query.

Schema:
{schema_context}

Sample Data:
{json.dumps(sample_rows[:3], indent=2)}

User Query:
{query}

CRITICAL RULES:
1. The DataFrame is pre-loaded as `df`. Do NOT read any file.
2. Store your final computation in a dictionary variable named `result`:
   `result = {{'data': <list of dicts or records>, 'summary': '<1-2 sentence findings>', 'chart_type': 'bar'|'line'|'pie'|'area'|'scatter'|'none'}}`
3. Never import `os`, `sys`, `subprocess`, `requests`, `eval`, or `exec`. Use only `pandas`, `numpy`, `math`, `json`, `datetime`.
4. Output valid JSON only with keys: "explanation", "code", "chart_type".
"""
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return self._parse_json_response(response.text)

    async def diagnose_and_repair(
        self,
        query: str,
        schema_context: str,
        failed_code: str,
        error_type: str,
        error_message: str,
        traceback_str: str
    ) -> Dict[str, Any]:
        from google import genai
        client = genai.Client(api_key=self.api_key)

        prompt = f"""
You are an expert Self-Healing AI Code Repair Agent.
The previously generated Python code failed during execution. Diagnose the exact root cause and generate a repaired version.

Dataset Schema:
{schema_context}

Original User Query:
{query}

Failed Python Code:
```python
{failed_code}
```

Error Type: {error_type}
Error Message: {error_message}
Traceback:
{traceback_str}

REPAIR INSTRUCTIONS:
1. Diagnose why it failed (e.g. column name typo, datetime parsing, division by zero, non-existent index).
2. Write corrected Python code that runs on `df` and populates `result = {{'data': ..., 'summary': ..., 'chart_type': ...}}`.
3. Output valid JSON only with keys: "diagnosis", "repaired_code", "explanation", "chart_type".
"""
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return self._parse_json_response(response.text)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        # Strip markdown fences if present
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        try:
            return json.loads(clean)
        except Exception:
            return {
                "explanation": "Generated response from Gemini.",
                "code": clean,
                "chart_type": "bar"
            }


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str, model_name: str = "gpt-4o-mini"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def generate_code(
        self,
        query: str,
        schema_context: str,
        sample_rows: list[dict],
        force_error: bool = False
    ) -> Dict[str, Any]:
        prompt = f"""
You are an expert Data Scientist and Python/Pandas developer.
Given the dataset schema and sample rows below, write executable Python code to answer the user query.

Schema:
{schema_context}

Sample Data:
{json.dumps(sample_rows[:3], indent=2)}

User Query:
{query}

CRITICAL EXECUTION RULES:
1. The DataFrame is pre-loaded as `df`. Do NOT read any file. Do NOT call pd.read_csv(), read_table(), open(), or import csv.
2. Store your final computation in a dictionary variable named `result`:
   `result = {{'data': <list of dicts or records>, 'summary': '<1-2 sentence findings>', 'chart_type': 'bar'|'line'|'pie'|'area'|'scatter'|'none'}}`
3. Never import `os`, `sys`, `subprocess`, `requests`, `eval`, or `exec`. Use only `pandas`, `numpy`, `math`, `json`, `datetime`.
4. Output valid JSON only with keys: "explanation", "code", "chart_type".
"""
        res = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a Python data analysis agent. Output valid JSON only. df is pre-loaded; never read files."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)

    async def diagnose_and_repair(
        self,
        query: str,
        schema_context: str,
        failed_code: str,
        error_type: str,
        error_message: str,
        traceback_str: str
    ) -> Dict[str, Any]:
        prompt = f"""
You are an expert Self-Healing AI Code Repair Agent.
The previously generated Python code failed during execution. Diagnose the exact root cause and generate a repaired version.

Dataset Schema:
{schema_context}

Original User Query:
{query}

Failed Python Code:
```python
{failed_code}
```

Error Type: {error_type}
Error Message: {error_message}
Traceback:
{traceback_str}

REPAIR INSTRUCTIONS:
1. Diagnose why it failed (e.g. column name typo, datetime parsing, division by zero, non-existent index).
2. Write corrected Python code that runs on `df` and populates `result = {{'data': ..., 'summary': ..., 'chart_type': ...}}`.
3. CRITICAL: `df` is already in memory. Do NOT read files from disk or use open() or pd.read_csv().
4. Output valid JSON only with keys: "diagnosis", "repaired_code", "explanation", "chart_type".
"""
        res = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a self-healing AI code repair agent. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    name = (provider_name or settings.DEFAULT_LLM_PROVIDER).lower()
    if name == "gemini" and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
    elif name in ["openai", "groq"] and settings.OPENAI_API_KEY:
        return OpenAICompatibleLLMProvider(settings.OPENAI_API_KEY, settings.OPENAI_BASE_URL, settings.OPENAI_MODEL)
    return MockLLMProvider()
