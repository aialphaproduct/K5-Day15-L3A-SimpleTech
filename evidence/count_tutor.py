"""Đếm bằng chứng pain cho A1 (tutor) từ data/preclass/chat.csv.
Chạy: python evidence/count_tutor.py "<đường dẫn tới data/preclass>"
Chỉ in số đã tổng hợp, không in nội dung học viên (data không có nội dung).
"""
import sys, os
import pandas as pd

folder = sys.argv[1] if len(sys.argv) > 1 else "data/preclass"
c = pd.read_csv(os.path.join(folder, "chat.csv"), encoding="utf-8-sig")
ta_q = c[(c.agent_id == "teaching_assistant") & (c.kind == "question")].copy()
ta_q["day"] = ta_q.transcript.str.extract(r"(Day\d+)")[0]

per = ta_q.groupby("hv").size().sort_values(ascending=False)
top10 = max(1, int(round(len(per) * 0.10)))

print("1. Tổng câu hỏi trợ giảng AI (kind=question, agent=teaching_assistant):", len(ta_q))
print("2. Học viên có ≥1 câu hỏi:", len(per))
print("3. Học viên chỉ hỏi đúng 1 câu:", int((per == 1).sum()), f"({(per == 1).mean()*100:.1f}%)")
print("4. Median câu / học viên:", per.median(), "· trung bình:", round(per.mean(), 1), "· max:", per.max())
print("5. Top 10% học viên hỏi nhiều nhất chiếm:", f"{per.iloc[:top10].sum() / per.sum() * 100:.1f}% câu hỏi")
print("6. Câu hỏi theo ngày học (day → số câu):")
print(ta_q.day.value_counts().sort_index().to_string())
print("7. 10 video có nhiều câu hỏi nhất (transcript → số câu):")
print(ta_q.transcript.value_counts().head(10).to_string())
print("8. Trả lời dùng lại từ câu cũ (cached=True):", f"{(ta_q.cached.astype(str) == 'True').mean()*100:.1f}%")
print("9. Dòng ghi rõ đoạn bài AI dựa vào (ngu_canh không trống):", int(ta_q.ngu_canh.notna().sum()), "/", len(ta_q))
print("10. Dòng có dùng gợi ý đã duyệt (guidance_ids khác []):",
      f"{(ta_q.guidance_ids.fillna('[]') != '[]').mean()*100:.1f}%")
print("11. Độ dài câu hỏi median (ký tự):", ta_q.do_dai_cau_hoi.median(),
      "· độ dài trả lời median:", ta_q.do_dai_tra_loi.median())
