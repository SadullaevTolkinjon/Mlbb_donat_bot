import requests
import json

SHEET_ID = "1H0nu3WXeM9PYaumP3or-N_WyNlKHJK9EWcAp6FA8KHQ"

def get_sheet_data(sheet_name):
    """Google Sheets dan ma'lumot olish"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={sheet_name}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        
        # JSON ni parse qilish
        json_str = response.text.split('(', 1)[1].rsplit(')', 1)[0]
        data = json.loads(json_str)
        
        rows = data['table']['rows']
        result = []
        
        # Barcha qatorlarni o'qish (headerdan boshlab)
        for row in rows:
            row_data = []
            for cell in row['c']:
                if cell is None:
                    row_data.append(None)
                else:
                    value = cell.get('v')
                    row_data.append(value)
            result.append(row_data)
        
        return result
    
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return None

def load_packages_from_sheets():
    """Barcha paketlarni yuklash"""
    
    # REGULAR_PACKAGES
    regular_data = get_sheet_data("REGULAR_PACKAGES")
    regular_packages = []
    if regular_data:
        for row in regular_data:
            # Headerdan skip qilish
            if not row[0] or row[0] == 'diamonds':
                continue
            if row[0] and row[1]:  # diamonds va price bor
                try:
                    regular_packages.append({
                        "diamonds": int(row[0]),
                        "price": int(row[1])
                    })
                except (ValueError, TypeError):
                    continue
    
    # DOUBLE_PACKAGES
    double_data = get_sheet_data("DOUBLE_PACKAGES")
    double_packages = []
    if double_data:
        for row in double_data:
            # Headerdan skip qilish
            if not row[0] or row[0] == 'diamonds':
                continue
            if row[0] and row[1] and row[2] and row[3]:
                try:
                    double_packages.append({
                        "diamonds": int(row[0]),
                        "bonus": int(row[1]),
                        "total": int(row[2]),
                        "price": int(row[3])
                    })
                except (ValueError, TypeError):
                    continue
    
    # WEEKLY_PASS
    weekly_data = get_sheet_data("WEEKLY_PASS")
    weekly_pass = []
    if weekly_data:
        for row in weekly_data:
            # Headerdan skip qilish
            if not row[0] or row[0] == 'name':
                continue
            if row[0] and row[1]:  # name va price bor
                try:
                    weekly_pass.append({
                        "name": str(row[0]),
                        "price": int(row[1]),
                        "description": str(row[2]) if row[2] else "",
                        "period": str(row[3]) if row[3] else "haftalik"
                    })
                except (ValueError, TypeError):
                    continue
    
    return regular_packages, double_packages, weekly_pass

def load_payment_info_from_sheets():
    """To'lov ma'lumotlarini yuklash"""
    payment_data = get_sheet_data("PAYMENT_INFO")
    
    payment_info = {
        "card": "8600 0000 0000 0000",  # Default
        "phone": "+998 90 000 00 00",   # Default
        "name": "ADMIN"                  # Default
    }
    
    if payment_data:
        for row in payment_data:
            # Headerdan skip qilish
            if not row[0] or row[0] == 'field':
                continue
            
            field = str(row[0]).lower()
            value = str(row[1]) if row[1] else ""
            
            if field in ['card', 'phone', 'name']:
                payment_info[field] = value
    
    return payment_info

# Test
# Test
if __name__ == "__main__":
    regular, double, weekly = load_packages_from_sheets()
    print("✅ REGULAR_PACKAGES:", regular)
    print(f"   Jami: {len(regular)} ta")
    print("✅ DOUBLE_PACKAGES:", double)
    print(f"   Jami: {len(double)} ta")
    print("✅ WEEKLY_PASS:", weekly)
    print(f"   Jami: {len(weekly)} ta")
    
    # Payment info test
    payment = load_payment_info_from_sheets()
    print("✅ PAYMENT_INFO:", payment)
 