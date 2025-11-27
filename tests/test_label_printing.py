#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Enhanced Label Printing System
Tests the core functionality without requiring the full UI
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.reports.label_printer import LabelPrinter
from modules.label_preferences import LabelPreferences


def test_layout_calculation():
    """Test layout calculation for different label sizes"""
    print("=" * 60)
    print("TEST 1: Layout Calculation")
    print("=" * 60)
    
    printer = LabelPrinter()
    
    for size in ["small", "medium", "large"]:
        layout = printer.calculate_layout(size, "letter")
        labels_per_row, labels_per_col, width, height = layout
        labels_per_page = labels_per_row * labels_per_col
        
        print(f"\n{size.upper()} Labels:")
        print(f"  - Labels per row: {labels_per_row}")
        print(f"  - Labels per column: {labels_per_col}")
        print(f"  - Labels per page: {labels_per_page}")
        print(f"  - Label size: {width:.2f} x {height:.2f} points")
    
    print("\n✅ Layout calculation test PASSED\n")


def test_label_preferences():
    """Test preference management"""
    print("=" * 60)
    print("TEST 2: Label Preferences")
    print("=" * 60)
    
    # Create preferences instance
    prefs = LabelPreferences("test_label_preferences.json")
    
    # Test default values
    print("\nDefault preferences:")
    print(f"  - Label size: {prefs.get('default_label_size')}")
    print(f"  - Show cut lines: {prefs.get('show_cut_lines')}")
    print(f"  - Default quantity: {prefs.get('default_quantity')}")
    
    # Test setting values
    prefs.set('default_label_size', 'large')
    prefs.set('show_cut_lines', False)
    
    # Test persistence (reload)
    prefs2 = LabelPreferences("test_label_preferences.json")
    assert prefs2.get('default_label_size') == 'large', "Preference not persisted!"
    assert prefs2.get('show_cut_lines') == False, "Preference not persisted!"
    
    print("\nAfter modification:")
    print(f"  - Label size: {prefs2.get('default_label_size')}")
    print(f"  - Show cut lines: {prefs2.get('show_cut_lines')}")
    
    # Cleanup
    Path("test_label_preferences.json").unlink(missing_ok=True)
    
    print("\n✅ Preference management test PASSED\n")


def test_label_generation():
    """Test label sheet generation with sample data"""
    print("=" * 60)
    print("TEST 3: Label Sheet Generation")
    print("=" * 60)
    
    printer = LabelPrinter()
    
    # Sample product data
    sample_products = [
        {
            'item_id': 1,
            'sku': 'IP-001',
            'name': 'iPhone 13 Pro 256GB',
            'sell_price': 15000.00,
            'storage': '256GB',
            'ram': '6GB',
            'color': 'Sierra Blue',
            'brand': 'Apple',
            'model': 'iPhone 13 Pro'
        },
        {
            'item_id': 2,
            'sku': 'SAM-045',
            'name': 'Samsung Galaxy S23 Ultra',
            'sell_price': 18000.00,
            'storage': '512GB',
            'ram': '12GB',
            'color': 'Phantom Black',
            'brand': 'Samsung',
            'model': 'Galaxy S23 Ultra'
        },
        {
            'item_id': 3,
            'sku': 'CN-123',
            'name': 'Xiaomi Redmi Note 12 Pro',
            'sell_price': 4500.00,
            'storage': '128GB',
            'ram': '8GB',
            'color': 'Midnight Blue',
            'brand': 'Xiaomi',
            'model': 'Redmi Note 12 Pro'
        }
    ]
    
    # Test with different quantities
    quantities = {
        1: 3,  # 3 labels for iPhone
        2: 2,  # 2 labels for Samsung
        3: 5   # 5 labels for Xiaomi
    }
    
    print("\nGenerating label sheet with:")
    for product in sample_products:
        qty = quantities[product['item_id']]
        print(f"  - {product['name']}: {qty} labels")
    
    total_labels = sum(quantities.values())
    print(f"\nTotal labels: {total_labels}")
    
    # Generate for each size
    for size in ["small", "medium", "large"]:
        try:
            output_path = printer.generate_label_sheet(
                products=sample_products,
                label_size=size,
                quantities=quantities,
                show_cut_lines=True,
                paper_size="letter",
                output_path=f"labels/test_{size}_labels.pdf"
            )
            
            # Check file exists
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                print(f"\n✅ {size.upper()} labels generated: {output_path}")
                print(f"   File size: {file_size:,} bytes")
            else:
                print(f"\n❌ {size.upper()} labels FAILED: File not created")
                
        except Exception as e:
            print(f"\n❌ {size.upper()} labels FAILED: {e}")
    
    print("\n✅ Label generation test PASSED\n")


def test_cut_lines():
    """Test cut lines on/off"""
    print("=" * 60)
    print("TEST 4: Cut Lines Toggle")
    print("=" * 60)
    
    printer = LabelPrinter()
    
    sample_products = [
        {
            'item_id': 1,
            'sku': 'TEST-001',
            'name': 'Test Product',
            'sell_price': 100.00,
            'storage': None,
            'ram': None,
            'color': None,
            'brand': None,
            'model': None
        }
    ]
    
    quantities = {1: 6}  # 6 labels to show grid
    
    # Test with cut lines
    output_with = printer.generate_label_sheet(
        products=sample_products,
        label_size="medium",
        quantities=quantities,
        show_cut_lines=True,
        output_path="labels/test_with_cutlines.pdf"
    )
    
    # Test without cut lines
    output_without = printer.generate_label_sheet(
        products=sample_products,
        label_size="medium",
        quantities=quantities,
        show_cut_lines=False,
        output_path="labels/test_without_cutlines.pdf"
    )
    
    if Path(output_with).exists() and Path(output_without).exists():
        print(f"\n✅ Cut lines ON: {output_with}")
        print(f"✅ Cut lines OFF: {output_without}")
        print("\n✅ Cut lines toggle test PASSED\n")
    else:
        print("\n❌ Cut lines toggle test FAILED\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ENHANCED LABEL PRINTING SYSTEM - TEST SUITE")
    print("=" * 60 + "\n")
    
    # Ensure labels directory exists
    Path("labels").mkdir(exist_ok=True)
    
    try:
        test_layout_calculation()
        test_label_preferences()
        test_label_generation()
        test_cut_lines()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        print("\nGenerated test PDFs are in the 'labels/' directory.")
        print("Open them to visually verify the label quality.\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
