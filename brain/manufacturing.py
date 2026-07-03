def analyze_manufacturing(jewelry_type, metal, stone_size_mm, production_type):
    result = {
        "jewelry_type": jewelry_type,
        "metal": metal,
        "stone_size_mm": stone_size_mm,
        "production_type": production_type,
        "recommendation": {},
        "warnings": [],
        "founder_logic": []
    }

    if jewelry_type == "female_ring":
        result["recommendation"]["min_width_mm"] = 2.0
        result["recommendation"]["min_thickness_mm"] = 1.2
        result["founder_logic"].append(
            "แหวนผู้หญิงควรเริ่มที่กว้าง 2 mm ขึ้นไป และหนาไม่ต่ำกว่า 1.2 mm แต่ต้องดูหน้างาน"
        )

    if production_type == "hot_rubber_mold":
        result["recommendation"]["shrinkage_allowance"] = "3%"
        result["founder_logic"].append(
            "อัดยางร้อนควรเผื่อทั้งชิ้นประมาณ 3%"
        )

    if production_type == "hot_silicone_mold":
        result["recommendation"]["shrinkage_allowance"] = "1.5%"
        result["founder_logic"].append(
            "ซิลิโคนร้อนควรเผื่อทั้งชิ้นประมาณ 1.5%"
        )

    if production_type == "cold_silicone_mold":
        result["recommendation"]["shrinkage_allowance"] = "0%"
        result["founder_logic"].append(
            "ซิลิโคนเย็นแทบไม่หด ไม่ต้องเผื่อ"
        )

    if stone_size_mm <= 1.3:
        result["recommendation"]["bead_size_mm"] = "0.5-0.6"
        result["recommendation"]["shared_spacing_mm"] = "0.15-0.20"
        result["founder_logic"].append(
            "งานไข่ปลา ค่ากลางที่เหมาะคือ 0.5-0.6 mm และเพชรไข่ปลาร่วมควรห่าง 0.15-0.20 mm"
        )

    if stone_size_mm > 2.0:
        result["warnings"].append(
            "ขนาดเพชรใหญ่ขึ้น ต้องตรวจความหนาและเนื้อสำหรับฝังเพิ่ม"
        )

    return result


if __name__ == "__main__":
    analysis = analyze_manufacturing(
        jewelry_type="female_ring",
        metal="18K",
        stone_size_mm=1.2,
        production_type="hot_rubber_mold"
    )

    print("PTR Manufacturing Brain V1")
    print("--------------------------------")
    for key, value in analysis.items():
        print(key, ":", value)