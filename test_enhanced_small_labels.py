#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for enhanced small labels with specifications
"""

from modules.reports.label_printer import LabelPrinter
from pathlib import Path

def test_enhanced_small_labels():
    """Test small labels with storage, RAM, and color specifications"""
    
    printer = LabelPrinter()
    
    # Test products with various specifications
    test_products = [
        {
            'item_id': 1,
            'sku': 'IP15-BLK-256',
            'barcode': 'IP15-BLK-256',
            'name': 'iPhone 15 Pro',
            'sell_price': 55000.00,
            'storage': '256GB',
            'ram': '8GB',
            'color': 'Black',
            'brand': 'Apple',
            'model': 'iPhone 15 Pro'
        },
        {
            'item_id': 2,
            'sku': 'SM-S23-512',
            'barcode': 'SM-S23-512',
            'name': 'Samsung Galaxy S23 Ultra',
            'sell_price': 48000.00,
            'storage': '512GB',
            'ram': '12GB',
            'color': 'Phantom Black',
            'brand': 'Samsung',
            'model': 'Galaxy S23 Ultra'
        },
        {
            'item_id': 3,
            'sku': 'XM-13P-128',
            'barcode': 'XM-13P-128',
            'name': 'Xiaomi 13 Pro',
            'sell_price': 25000.00,
            'storage': '128GB',
            'ram': '8GB',
            'color': 'White',
            'brand': 'Xiaomi',
            'model': '13 Pro'
        }
    ]
    
    # Generate small labels
    quantities = {p['item_id']: 2 for p in test_products}
    
    output_path = printer.generate_label_sheet(
        products=test_products,
        label_size="small",
        quantities=quantities,
        show_cut_lines=True,
        paper_size="letter"
    )
    
    print(f"✅ Enhanced small labels generated successfully!")
    print(f"📄 File: {output_path}")
    print(f"📦 Total labels: {sum(quantities.values())}")
    print(f"\nLabel details:")
    print(f"  - Product name (smaller font)")
    print(f"  - Specifications: Storage | RAM | Color")
    print(f"  - Price (medium-large)")
    print(f"  - Barcode (Code128)")
    
    # Verify file exists
    if Path(output_path).exists():
        print(f"\n✅ File verified: {Path(output_path).absolute()}")
        return True
    else:
        print(f"\n❌ File not found: {output_path}")
        return False

if __name__ == "__main__":
    success = test_enhanced_small_labels()
    exit(0 if success else 1)
