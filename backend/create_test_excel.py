#!/usr/bin/env python3
"""
Create test Excel file for Phase 4 Excel automation testing.

Generates a sample Excel file with:
- Multiple columns (商品名, 売上金額, 税込金額, 数量, 日付)
- Sample data rows
- Saved in backend/test_data/ directory
"""

from openpyxl import Workbook
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_excel():
    """Create test Excel file with sample data."""

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = '売上データ'

    # Headers
    headers = ['商品名', '売上金額', '税込金額', '数量', '日付']
    ws.append(headers)

    # Sample data rows
    data_rows = [
        ['ノートPC', 98000, 107800, 15, '2025-01-01'],
        ['マウス', 2500, 2750, 120, '2025-01-02'],
        ['キーボード', 4800, 5280, 45, '2025-01-03'],
        ['モニター', 35000, 38500, 28, '2025-01-04'],
        ['ヘッドセット', 8900, 9790, 36, '2025-01-05'],
        ['Webカメラ', 6500, 7150, 52, '2025-01-06'],
        ['USBケーブル', 800, 880, 200, '2025-01-07'],
        ['外付けHDD', 12000, 13200, 18, '2025-01-08'],
        ['メモリ', 15000, 16500, 65, '2025-01-09'],
        ['SSD', 18000, 19800, 42, '2025-01-10']
    ]

    for row in data_rows:
        ws.append(row)

    # Create test_data directory if not exists
    test_data_dir = Path(__file__).parent / 'test_data'
    test_data_dir.mkdir(exist_ok=True)

    # Save to Excel
    output_path = test_data_dir / 'sample_sales_data.xlsx'
    wb.save(output_path)

    logger.info(f"Test Excel file created: {output_path}")
    logger.info(f"Rows: {len(data_rows) + 1} (including header), Columns: {len(headers)}")

    return output_path


if __name__ == '__main__':
    create_test_excel()
