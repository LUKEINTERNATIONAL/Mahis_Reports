
import pandas as pd
from typing import Any, Dict, List, Tuple
from visualizations import create_sum, create_count, create_count_sets

class ReportTableBuilder:
    def __init__(self, excel_path: str, source_df: pd.DataFrame):
        self.excel_path = excel_path
        self.source_df = source_df

        self.vars_df: pd.DataFrame | None = None
        self.filters_df: pd.DataFrame | None = None
        self.filters_map: Dict[str, Any] = {}
        self._value_cache: Dict[str, str] = {}
        self._errors: List[str] = []
        self.report_name: pd.DataFrame | None = None

    def load_spec(self) -> None:
        xls = pd.ExcelFile(self.excel_path, engine="openpyxl")
        self.vars_df = pd.read_excel(xls, sheet_name="VARIABLE_NAMES", engine="openpyxl")
        self.filters_df = pd.read_excel(xls, sheet_name="FILTERS", engine="openpyxl")
        self.vars_df.columns = [str(c).strip() for c in self.vars_df.columns]
        self.filters_df.columns = [str(c).strip() for c in self.filters_df.columns]
        self.vars_df = self.vars_df.fillna("")
        self.filters_df = self.filters_df.fillna("")
        self.report_name = pd.read_excel(xls, sheet_name="REPORT_NAME", engine="openpyxl")
        self.report_name.columns = [str(c).strip() for c in self.report_name.columns]
        self._build_filters_map()

    def _build_filters_map(self) -> None:
        self.filters_map.clear()
        for _, row in self.filters_df.iterrows():
            fname = str(row.get("filter_name", "")).strip()
            if not fname:
                continue
            measure = str(row.get("measure", "")).strip().lower()
            num_field = str(row.get("num_field", "ValueN")).strip()
            unique_column = str(row.get("unique_column", "encounter_id")).strip()
            pairs: List[Tuple[str, Any]] = []
            for i in range(1, 10):
                fcol = str(row.get(f"variable{i}", "")).strip()
                if not fcol:
                    continue
                fval = row.get(f"value{i}", "")
                parsed_val = self._parse_filter_value(fval)
                pairs.append((fcol, parsed_val))
            self.filters_map[fname] = {
                "measure": measure,
                "num_field": num_field,
                "unique_column": unique_column,
                "pairs": pairs,
            }

    @staticmethod
    def _parse_filter_value(val: Any) -> Any:
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return ""
            if s.startswith("[") and s.endswith("]"):
                inner = s[1:-1].strip()
                return [] if not inner else [x.strip() for x in inner.split(",")]
            if "|" in s:
                return [x.strip() for x in s.split("|")]
            # if "," in s:
            #     return [x.strip() for x in s.split(",")]
        return val

    def _compute_value_from_filter(self, filter_name: str) -> str:
        if not filter_name:
            return ""
        if filter_name in self._value_cache:
            return self._value_cache[filter_name]
        if filter_name not in self.filters_map:
            self._errors.append(f"FILTERS row not found: '{filter_name}'")
            self._value_cache[filter_name] = "N/A"
            return "N/A"

        spec = self.filters_map[filter_name]
        measure = spec["measure"]
        args: List[Any] = [self.source_df]

        if measure == "sum":
            args.append(spec["num_field"])
            for fcol, fval in spec["pairs"]:
                args.extend([fcol, fval])
            result = create_sum(*args)
        elif measure == "count_set":
            args.append(spec["unique_column"])
            for fcol, fval in spec["pairs"]:
                args.extend([fcol, fval])
            result = create_count_sets(*args)
        else:  # count
            args.append(spec["unique_column"])
            for fcol, fval in spec["pairs"]:
                args.extend([fcol, fval])
            result = create_count(*args)

        result_str = "" if result is None else str(result)
        self._value_cache[filter_name] = result_str
        return result_str

    def _collect_value_columns(self) -> List[str]:
        return sorted([c for c in self.vars_df.columns if c.lower().startswith("value_")])
    def _title(self) -> str:
        if self.report_name is None or "name" not in self.report_name.columns:
            return "Report"
        vals = [str(v).strip() for v in self.report_name["name"].tolist() if str(v).strip()]
        return vals[0] if vals else "Report"

    def build_section_tables(self) -> List[Tuple[str, pd.DataFrame]]:
        value_cols = self._collect_value_columns()
        sections: List[Tuple[str, pd.DataFrame]] = []
        current_section_name = ""
        current_headers: Dict[str, str] = {}
        buffer: List[Dict[str, Any]] = []

        for _, row in self.vars_df.iterrows():
            row_type = str(row.get("type", "")).strip().lower()
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            if row_type == "section":
                if buffer:
                    df = pd.DataFrame(buffer)
                    df = df.loc[:, (df != "").any(axis=0)]
                    sections.append((current_section_name, df))
                    buffer = []
                current_section_name = name
                current_headers = {}
                for vc in value_cols:
                    header_val = str(row.get(vc, "")).strip()
                    if header_val:
                        current_headers[vc] = header_val
                continue

            out = {"Data Element": name}
            for vc in value_cols:
                filter_ref = str(row.get(vc, "")).strip()
                out[current_headers.get(vc, vc)] = (
                    self._compute_value_from_filter(filter_ref) if filter_ref else ""
                )
            buffer.append(out)

        if buffer:
            df = pd.DataFrame(buffer)
            df = df.loc[:, (df != "").any(axis=0)]
            sections.append((current_section_name, df))

        return sections

    
    def build_dash_components(self) -> List[Any]:
        from dash import html, dash_table

        title = self._title() or "Report"  # Or use self._title() if DESIGN sheet still has Title
        sections = self.build_section_tables()  # New method for multi-section tables

        children: List[Any] = [html.H1(title, style={"textAlign": "center"})]

        for subtitle, subdf in sections:
            if subtitle:
                children.append(html.H2(subtitle, style={"marginBottom": "0px"}))

            value_cols = [c for c in subdf.columns if c != "Data Element"]
            columns = [{"name": "Data Element", "id": "Data Element"}]
            for cid in value_cols:
                columns.append({"name": cid, "id": cid})

            children.append(
                dash_table.DataTable(
                    data=subdf.to_dict("records"),
                    columns=columns,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "padding": "6px",
                        "fontFamily": "Segoe UI, Arial, sans-serif",
                        "fontSize": "14px",
                        "border": "1px solid #e9ecef",
                        "minWidth": "120px",
                    },
                    style_header={
                        "backgroundColor": "#198754",
                        "fontWeight": "bold",
                        "border": "1px solid #dee2e6",
                        "color": "#ffffff",
                        "textAlign": "center"
                    },
                    style_data_conditional=[
                        {"if": {"column_id": "Data Element"}, "textAlign": "left", "fontWeight": "600"},
                        *[{"if": {"column_id": cid}, "textAlign": "center"} for cid in value_cols],
                        # Grey background for empty cells
                        {"if": {"column_id": "Data Element", "filter_query": "{Data Element} = ''"}, "backgroundColor": "#f1f3f4"},
                        *[
                            {"if": {"column_id": cid, "filter_query": f"{{{cid}}} = ''"}, "backgroundColor": "#f1f3f4"}
                            for cid in value_cols
                        ]
                    ]
                )
            )

        # Optional: show any parsing errors below the tables
        if self._errors:
            children.append(
                html.Div(
                    [html.Small(e) for e in self._errors],
                    style={"color": "#b02a37", "marginTop": "8px"}
                )
            )

        return children




# # reports_class.py

# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Dict, List, Optional, Tuple

# import pandas as pd
# from dash import html
# from dash import dash_table

# from visualizations import create_sum, create_count, create_count_sets


# @dataclass
# class FilterSpec:
#     name: str
#     measure: str  # 'sum', 'count_set' or 'count'
#     num_field: Optional[str] = None        # for sum
#     unique_column: Optional[str] = None    # for count
#     pairs: List[Tuple[Optional[str], Optional[Any]]] = None


# class ReportTableBuilder:
#     """
#     Build a Dash DataTable from an Excel spec.

#     DESIGN:
#       - Title (string)
#       - SubTitle (0..n rows, optional)
#       - rows_per_section (optional)
#       - value_* columns: the first non-empty cell in each such column is the display header.
#         The presence of non-empty header means include that column.
#         Example: value_1x1 = 'Under 5', value_1x2 = 'Over 5'

#     VARIABLE_NAMES:
#       - name (indicator label)
#       - value_* cells contain filter_name keys referencing FILTERS
#       - Optional: Section

#     FILTERS:
#       - filter_name
#       - measure ('sum'/'count'/'count_set')
#       - num_field (for 'sum'); also accepts legacy 'value_column'
#       - unique_column (optional for 'count', defaults to 'encounter_id')
#       - filter_col_1..6, filter_val_1..6
#     """

#     def __init__(self, excel_path: str, source_df: pd.DataFrame):
#         self.excel_path = excel_path
#         self.source_df = source_df

#         self.design_df: Optional[pd.DataFrame] = None
#         self.vars_df: Optional[pd.DataFrame] = None
#         self.filters_df: Optional[pd.DataFrame] = None
#         self.filters_map: Dict[str, FilterSpec] = {}

#         # caches / state
#         self._value_cache: Dict[str, str] = {}
#         self._design_value_cols: List[Tuple[str, str]] = []  # [(col_id, header_name)]
#         self._errors: List[str] = []

#     # -----------------------------
#     # Load spec
#     # -----------------------------
#     def load_spec(self) -> None:
#         xls = pd.ExcelFile(self.excel_path, engine="openpyxl")

#         required = ["DESIGN", "VARIABLE_NAMES", "FILTERS"]
#         missing = [s for s in required if s not in xls.sheet_names]
#         if missing:
#             raise ValueError(f"Missing sheet(s): {', '.join(missing)}")

#         self.design_df = pd.read_excel(xls, sheet_name="DESIGN", engine="openpyxl")
#         self.vars_df = pd.read_excel(xls, sheet_name="VARIABLE_NAMES", engine="openpyxl")
#         self.filters_df = pd.read_excel(xls, sheet_name="FILTERS", engine="openpyxl")

#         # Normalize
#         self.design_df.columns = [str(c).strip() for c in self.design_df.columns]
#         self.vars_df.columns = [str(c).strip() for c in self.vars_df.columns]
#         self.filters_df.columns = [str(c).strip() for c in self.filters_df.columns]
#         self.vars_df = self.vars_df.fillna("")
#         self.filters_df = self.filters_df.fillna("")

#         # Read design-driven value columns (must happen before building table)
#         self._design_value_cols = self._design_value_columns()

#         self._build_filters_map()

#     # -----------------------------
#     # DESIGN-driven value columns
#     # -----------------------------
#     def _design_value_columns(self) -> List[Tuple[str, str]]:
#         """
#         Returns a list of (value_col_id, header_name) in the order found in DESIGN.
#         Only includes value_* columns that have a non-empty header in any row.
#         Example result: [('value_1x1', 'Under 5'), ('value_1x2', 'Over 5')]
#         """
#         if self.design_df is None:
#             return []

#         # Candidate columns
#         cand_cols = [c for c in self.design_df.columns if str(c).lower().startswith("value_")]
#         if not cand_cols:
#             return []

#         # Sort naturally (value_1x1, value_1x2, value_2x1, ...)
#         def sort_key(c: str):
#             parts = c.replace("value_", "").split("x")
#             nums = []
#             for p in parts:
#                 try:
#                     nums.append(int(p))
#                 except Exception:
#                     nums.append(0)
#             return nums

#         cand_cols = sorted(cand_cols, key=sort_key)

#         result: List[Tuple[str, str]] = []
#         for col in cand_cols:
#             # First non-empty cell is the header
#             header = ""
#             for v in self.design_df[col].tolist():
#                 s = str(v).strip()
#                 if s and s.lower() != "nan":
#                     header = s
#                     break
#             if header:
#                 result.append((col, header))

#         return result  # may be empty; we’ll fallback later

#     # -----------------------------
#     # FILTERS map
#     # -----------------------------
#     def _build_filters_map(self) -> None:
#         self.filters_map.clear()

#         for _, row in self.filters_df.iterrows():
#             fname = str(row.get("filter_name", "")).strip()
#             if not fname:
#                 continue

#             measure = str(row.get("measure", "")).strip().lower()
#             if measure not in {"sum", "count","count_set"}:
#                 raise ValueError(f"FILTERS[{fname}]: invalid measure '{measure}'")

#             num_field = None
#             unique_column = None

#             if measure == "sum":
#                 # Accept 'num_field' or legacy 'value_column'; fallback to 'ValueN'
#                 nf = str(row.get("unique_column", "")).strip()
#                 # if not nf:
#                 #     nf = str(row.get("unique_column", "")).strip()
#                 if not nf:
#                     nf = "ValueN"
#                 num_field = nf
#             else:
#                 uc = str(row.get("unique_column", "")).strip()
#                 unique_column = uc if uc else "encounter_id"

#             pairs: List[Tuple[Optional[str], Optional[Any]]] = []
#             for i in range(1, 7):
#                 col_key = f"variable{i}"
#                 val_key = f"value{i}"
                
#                 fcol = str(row.get(col_key, "")).strip()
#                 if not fcol:
#                     continue  # <-- skip; do NOT append (None, None)

#                 fval = row.get(val_key, "")
#                 parsed_val = self._parse_filter_value(fval)
#                 pairs.append((fcol, parsed_val))


#             self.filters_map[fname] = FilterSpec(
#                 name=fname,
#                 measure=measure,
#                 num_field=num_field,
#                 unique_column=unique_column,
#                 pairs=pairs,
#             )

#     @staticmethod
#     def _parse_filter_value(val: Any) -> Any:
#         if isinstance(val, list):
#             return val
#         if isinstance(val, str):
#             s = val.strip()
#             if not s:
#                 return ""
#             if s.startswith("[") and s.endswith("]"):
#                 inner = s[1:-1].strip()
#                 return [] if not inner else [x.strip() for x in inner.split(",")]
#             if "|" in s:
#                 return [x.strip() for x in s.split("|")]
#             # if "," in s:
#             #     return [x.strip() for x in s.split(",")]
#         return val

#     # -----------------------------
#     # Compute value using FILTERS
#     # -----------------------------
#     def _compute_value_from_filter(self, filter_name: str) -> str:
#         if not filter_name:
#             return ""

#         # cache
#         if filter_name in self._value_cache:
#             return self._value_cache[filter_name]

#         if filter_name not in self.filters_map:
#             msg = f"FILTERS row not found: '{filter_name}'"
#             self._errors.append(msg)
#             self._value_cache[filter_name] = "N/A"
#             return "N/A"

#         spec = self.filters_map[filter_name]

#         if spec.measure == "sum":
#             args: List[Any] = [self.source_df, spec.num_field]

#             for fcol, fval in spec.pairs:
#                 args.extend([fcol, fval])
#             result = create_sum(*args)
#             # print(result)
#         elif spec.measure == "count_set":  # count_set
#             args = [self.source_df, spec.unique_column]
#             for fcol, fval in spec.pairs:
#                 args.extend([fcol, fval])
#             result = create_count_sets(*args)
#         else:  # count
#             args = [self.source_df, spec.unique_column]
#             for fcol, fval in spec.pairs:
#                 args.extend([fcol, fval])
#             result = create_count(*args)

#         result_str = "" if result is None else str(result)
#         self._value_cache[filter_name] = result_str
#         return result_str

#     # -----------------------------
#     # Value columns selection
#     # -----------------------------
    
#     def _collect_value_columns(self) -> List[str]:
#         value_cols = [c for c in self.vars_df.columns if str(c).lower().startswith("value_")]
#         def sort_key(c: str):
#             parts = c.replace("value_", "").split("x")
#             nums = []
#             for p in parts:
#                 try:
#                     nums.append(int(p))
#                 except Exception:
#                     nums.append(0)
#             return nums
#         return sorted(value_cols, key=sort_key)


    
#     def _value_column_headers(self, col_ids: List[str]) -> Dict[str, str]:
#         headers = {}
#         for cid in col_ids:
#             header = ""
#             for _, row in self.vars_df.iterrows():
#                 val = str(row.get(cid, "")).strip()
#                 if val:
#                     header = val
#                     break
#             headers[cid] = header if header else cid.replace("_", " ").title()
#         return headers


#     # -----------------------------
#     # Build the table DF
#     # -----------------------------
    
#     def build_table_dataframe(self) -> pd.DataFrame:
#         if self.vars_df is None:
#             raise RuntimeError("Call load_spec() first.")

#         value_cols = self._collect_value_columns()
#         rows: List[Dict[str, Any]] = []

#         for _, row in self.vars_df.iterrows():
#             row_type = str(row.get("type", "")).strip().lower()
#             name = str(row.get("name", "")).strip()
#             if not name:
#                 continue

#             if row_type == "section":
#                 out = {"name": name}
#                 for vc in value_cols:
#                     out[vc] = ""  # leave empty for section rows
#                 rows.append(out)
#                 continue

#             out = {"name": name}
#             for vc in value_cols:
#                 filter_ref = str(row.get(vc, "")).strip() if vc in row else ""
#                 out[vc] = self._compute_value_from_filter(filter_ref) if filter_ref else ""
#             rows.append(out)

#         return pd.DataFrame(rows)


#     # -----------------------------
#     # Sections & title
#     # -----------------------------
#     def _title(self) -> str:
#         if self.design_df is None or "Title" not in self.design_df.columns:
#             return "Report"
#         vals = [str(v).strip() for v in self.design_df["Title"].tolist() if str(v).strip()]
#         return vals[0] if vals else "Report"

#     def _design_subtitles(self) -> List[str]:
#         if self.design_df is None or "SubTitle" not in self.design_df.columns:
#             return []
#         return [str(v).strip() for v in self.design_df["SubTitle"].tolist() if str(v).strip()]

#     def _rows_per_section(self) -> Optional[int]:
#         if self.design_df is None:
#             return None
#         for c in self.design_df.columns:
#             if str(c).lower() == "rows_per_section":
#                 s = self.design_df[c].dropna().astype(str)
#                 for v in s:
#                     try:
#                         return int(float(v))
#                     except Exception:
#                         pass
#         return None

    
    
#     def _split_sections(self, table_df: pd.DataFrame) -> List[Tuple[str, pd.DataFrame]]:
#         sections: List[Tuple[str, pd.DataFrame]] = []
#         current_section = ""
#         buffer: List[Dict[str, Any]] = []

#         for _, row in table_df.iterrows():
#             # Detect section marker: all value_* columns empty and name present
#             if all(str(row[c]).strip() == "" for c in table_df.columns if c != "name") and row["name"]:
#                 # Flush previous buffer
#                 if buffer:
#                     sections.append((current_section or "Section", pd.DataFrame(buffer)))
#                     buffer = []
#                 current_section = row["name"]
#             else:
#                 buffer.append(row.to_dict())

#         # Flush remaining rows
#         if buffer:
#             sections.append((current_section or "Section", pd.DataFrame(buffer)))

#         return sections




#     # -----------------------------
#     # Public: Dash components
#     # -----------------------------
#     def build_dash_components(self) -> List[Any]:
#         title = self._title()
#         table_df = self.build_table_dataframe()

#         value_cols = [c for c in table_df.columns if c != "name"]
#         headers = self._value_column_headers(value_cols)

#         columns = [{"name": "Data Element", "id": "name"}]
#         for cid in value_cols:
#             columns.append({"name": headers.get(cid, cid), "id": cid})

#         sections = self._split_sections(table_df)

#         children: List[Any] = [html.H1(title, style={"textAlign": "center"})]
#         for subtitle, subdf in sections:
#             if subtitle:
#                 children.append(html.H2(subtitle, style={"marginTop": "0px"}))

#             children.append(
#                 dash_table.DataTable(
#                     data=subdf.to_dict("records"),
#                     columns=columns,
#                     style_table={"overflowX": "auto"},
#                     style_cell={
#                         "padding": "6px",
#                         "fontFamily": "Segoe UI, Arial, sans-serif",
#                         "fontSize": "14px",
#                         "border": "1px solid #e9ecef",
#                         "minWidth": "120px",
#                     },
#                     style_header={
#                         "backgroundColor": "#198754",
#                         "fontWeight": "bold",
#                         "border": "1px solid #dee2e6",
#                         "color": "#ffffff",
#                         "textAlign": "center"
#                     },
#                     style_data_conditional=[
#                         {"if": {"column_id": "name"}, "textAlign": "left", "fontWeight": "600"},
#                         *[{"if": {"column_id": cid}, "textAlign": "center"} for cid in value_cols],
#                         # Grey background for empty cells
#                         {"if": {"column_id": "name", "filter_query": "{name} = ''"}, "backgroundColor": "#f1f3f4"},
#                         *[
#                             {"if": {"column_id": cid, "filter_query": f"{{{cid}}} = ''"}, "backgroundColor": "#f1f3f4"}
#                             for cid in value_cols
#                         ]
#                     ]
#                 )

                
#             )

#         # Optional: show any parsing errors below the table
#         if self._errors:
#             children.append(
#                 html.Div(
#                     [html.Small(e) for e in self._errors],
#                     style={"color": "#b02a37", "marginTop": "8px"}
#                 )
#             )

#         return children