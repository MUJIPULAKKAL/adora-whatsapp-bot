def format_line(label, value):
    return f"- {label.ljust(22)} = {value}"

def format_item(width, height, pcs, area):
    return f"- W {width:<5.2f} x H {height:<5.2f} {str(pcs).rjust(2)} Pcs = {area:>6.2f} m²"

def calculate_invoice(width, height, pcs=1, unit_price=40, min_area=1.5):
    area_per_piece = width * height
    if area_per_piece < min_area:
        area_per_piece = min_area

    total_area = area_per_piece * pcs
    net = total_area * unit_price
    vat = net * 0.05
    total = net + vat

    invoice = "**Adora Blinds Invoice**\n"
    invoice += "- Product: Roller Blind Blackout\n"
    invoice += format_item(width, height, pcs, total_area) + "\n"
    invoice += format_line("Total Area", f"{total_area:.2f} m²") + "\n"
    invoice += format_line("Unit Price", f"{unit_price:.2f} AED/m²") + "\n"
    invoice += format_line("Net Amount", f"{net:.2f} AED") + "\n"
    invoice += format_line("VAT (5%)", f"{vat:.2f} AED") + "\n"
    invoice += format_line("Total Amount", f"{total:.2f} AED") + "\n"
    invoice += format_line("Delivery Method", "Free Delivery")
    return invoice

def calculate_multi_invoice(order_text, unit_price=40, min_area=1.5):
    items = order_text.split(",")
    summary = {}
    total_area = 0
    net_amount = 0

    for item in items:
        try:
            width, height, pcs = item.split("x")
            width, height, pcs = float(width), float(height), int(pcs)

            area_per_piece = width * height
            if area_per_piece < min_area:
                area_per_piece = min_area

            line_area = area_per_piece * pcs

            key = f"{width:.2f}x{height:.2f}"
            if key in summary:
                summary[key]["pcs"] += pcs
                summary[key]["area"] += line_area
            else:
                summary[key] = {"width": width, "height": height, "pcs": pcs, "area": line_area}

            total_area += line_area
            net_amount += line_area * unit_price

        except Exception:
            return "❌ Invalid format. Use: order 2.5x3.5x1,1.5x1.0x2"

    vat = net_amount * 0.05
    total = net_amount + vat

    invoice = "**Adora Blinds Invoice**\n"
    invoice += "- Product: Roller Blind Blackout\n"
    for val in summary.values():
        invoice += format_item(val['width'], val['height'], val['pcs'], val['area']) + "\n"

    invoice += format_line("Total Area", f"{total_area:.2f} m²") + "\n"
    invoice += format_line("Unit Price", f"{unit_price:.2f} AED/m²") + "\n"
    invoice += format_line("Net Amount", f"{net_amount:.2f} AED") + "\n"
    invoice += format_line("VAT (5%)", f"{vat:.2f} AED") + "\n"
    invoice += format_line("Total Amount", f"{total:.2f} AED") + "\n"
    invoice += format_line("Delivery Method", "Free Delivery")
    return invoice
