# add_product_barcodes.py
"""
Quick tool to add barcodes to products
"""

from modules.barcode_manager import add_barcode, get_all_barcodes_for_item
from modules.db import get_conn

def list_products():
    """List all products"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id, sku, name, sell_price FROM inventory ORDER BY item_id")
    products = c.fetchall()
    conn.close()
    
    print("\n" + "="*80)
    print("AVAILABLE PRODUCTS")
    print("="*80)
    print(f"{'ID':<5} {'SKU':<15} {'Name':<40} {'Price':<15}")
    print("-"*80)
    
    for p in products:
        print(f"{p[0]:<5} {p[1]:<15} {p[2]:<40} {p[3]:<15,.2f} EGP")
    
    print("="*80)
    return products

def add_barcodes_interactive():
    """Interactive barcode addition"""
    print("\n🔍 BARCODE MANAGEMENT TOOL")
    print("="*80)
    
    # List products
    products = list_products()
    
    if not products:
        print("\n❌ No products found. Add products to inventory first.")
        return
    
    # Get product ID
    try:
        item_id = int(input("\nEnter Product ID: "))
    except ValueError:
        print("❌ Invalid ID")
        return
    
    # Verify product exists
    product = None
    for p in products:
        if p[0] == item_id:
            product = p
            break
    
    if not product:
        print(f"❌ Product ID {item_id} not found")
        return
    
    print(f"\n✓ Selected: {product[2]} (SKU: {product[1]})")
    
    # Show existing barcodes
    existing = get_all_barcodes_for_item(item_id)
    if existing:
        print(f"\n📋 Existing Barcodes: {len(existing)}")
        for bc in existing:
            print(f"  • {bc[1]} | Serial: {bc[2] or 'N/A'} | Status: {bc[3]}")
    else:
        print("\n📋 No barcodes added yet")
    
    # Add barcodes
    print("\n" + "="*80)
    print("ADD BARCODES")
    print("="*80)
    print("Enter barcodes one per line (or 'done' to finish)")
    print("Format: barcode [serial_number]")
    print("Example: 8901234567890 356789012345671")
    print("-"*80)
    
    added = 0
    failed = 0
    
    while True:
        line = input("Barcode: ").strip()
        
        if line.lower() in ['done', 'exit', 'quit', '']:
            break
        
        # Parse input
        parts = line.split()
        barcode = parts[0]
        serial = parts[1] if len(parts) > 1 else None
        
        # Add barcode
        if add_barcode(item_id, barcode, serial):
            print(f"  ✓ Added: {barcode}" + (f" | Serial: {serial}" if serial else ""))
            added += 1
        else:
            print(f"  ❌ Failed: {barcode} (may already exist)")
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Successfully added: {added}")
    print(f"❌ Failed: {failed}")
    print(f"📦 Total barcodes for {product[2]}: {len(existing) + added}")
    print("="*80)

def bulk_add_from_file():
    """Add barcodes from CSV file"""
    print("\n📁 BULK IMPORT FROM FILE")
    print("="*80)
    
    filename = input("Enter CSV filename (e.g., barcodes.csv): ").strip()
    
    try:
        import csv
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            
            added = 0
            failed = 0
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                item_id = int(row[0])
                barcode = row[1]
                serial = row[2] if len(row) > 2 else None
                
                if add_barcode(item_id, barcode, serial):
                    print(f"✓ Added: {barcode}")
                    added += 1
                else:
                    print(f"❌ Failed: {barcode}")
                    failed += 1
            
            print(f"\n✓ Added: {added}, ❌ Failed: {failed}")
    
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("BARCODE MANAGEMENT TOOL")
        print("="*80)
        print("1. Add barcodes interactively")
        print("2. Bulk import from CSV")
        print("3. List products")
        print("4. Exit")
        print("="*80)
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            add_barcodes_interactive()
        elif choice == '2':
            bulk_add_from_file()
        elif choice == '3':
            list_products()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
